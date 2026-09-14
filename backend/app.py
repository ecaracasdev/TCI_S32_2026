from fastapi import FastAPI, Request
from pathlib import Path
import argparse
import uvicorn
from config import Config
from logs import get_logger, load_logger
from utils import load_config, get_config, update_config

def create_app(app_name: str = "app", description: str = "---", cfg: Config = None) -> FastAPI:
    """
    Construye y configura el app. Separado de __main__ para poder
    importarlo en tests sin efectos secundarios.
    """
    from contextlib import asynccontextmanager
    from fastapi.middleware.cors import CORSMiddleware
    from starlette.middleware.sessions import SessionMiddleware
    from fastapi_keycloak_middleware import (
        KeycloakConfiguration,
        setup_keycloak_middleware,
    )
    from routers import routers
    from services import get_auth_service, get_db_service
    from auth_utils import map_keycloak_user
    if cfg is None:
        get_logger().critical("Archivo de Configuración No cargado, no se puede crear la APP")
        exit()
        
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger = get_logger()
        try:
            # Inicialización de recursos (DB pool, caché, etc.)
            db_service = get_db_service()
            auth_service = get_auth_service()
            
            logger.info("Startup OK")
        except Exception as e:
            logger.critical(f"Startup failed: {e}")
            raise  # no silenciar — que falle fuerte y temprano
        yield
        # Teardown
        logger.info("Shutdown OK")
        
    def _build_cors_origins(cors_urls: list[str]) -> list[str]:
        origins: list[str] = []
        for raw in cors_urls:
            value = raw.strip()
            if not value:
                continue
            if value.startswith("http://") or value.startswith("https://"):
                origins.append(value)
                continue
            origins.append(f"http://{value}")
            origins.append(f"https://{value}")
        return sorted(set(origins))

    def _load_routers(app: FastAPI, restrict_modules: list[str] = []) -> int:
        active = 0
        for router in routers:
            if router.prefix.strip("/") in restrict_modules:
                continue
            app.include_router(router)
            active += 1
        return active

    # app.mount("/static", StaticFiles(directory="static"), name="static")
    app = FastAPI(
        title=app_name,
        description=description,
        lifespan=lifespan,
        version=cfg.server.VERSION
    )
    
    _load_routers(app, cfg.server.RESTRICTED_MODULES)

    auth_cfg = get_config().auth
    keycloak_cfg = auth_cfg.KEYCLOAK
    if auth_cfg.ENABLED and keycloak_cfg.ENABLED:
        keycloak_configuration = KeycloakConfiguration(
            url=keycloak_cfg.URL,
            realm=keycloak_cfg.REALM,
            client_id=keycloak_cfg.CLIENT_ID,
            client_secret=keycloak_cfg.CLIENT_SECRET,
            verify=keycloak_cfg.VERIFY,
            authentication_scheme=keycloak_cfg.AUTHENTICATION_SCHEME,
            validate_token=keycloak_cfg.VALIDATE_TOKEN,
            claims=keycloak_cfg.CLAIMS,
            reject_on_missing_claim=keycloak_cfg.REJECT_ON_MISSING_CLAIM,
            swagger_client_id=keycloak_cfg.SWAGGER_CLIENT_ID or None,
        )
        setup_keycloak_middleware(
            app,
            keycloak_configuration=keycloak_configuration,
            user_mapper=map_keycloak_user,
            exclude_patterns=keycloak_cfg.EXCLUDE_PATTERNS,
            add_swagger_auth=keycloak_cfg.ADD_SWAGGER_AUTH,
        )

    # CORS must be added after authentication so it handles OPTIONS preflight
    # requests before the Keycloak middleware looks for a Bearer token.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_build_cors_origins(get_config().server.CORS_URLS),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Keep the generic session-based OAuth flow available for legacy projects,
    # but do not combine it with the header-based Keycloak flow.
    if auth_cfg.ENABLED and auth_cfg.OAUTH.ENABLED and not keycloak_cfg.ENABLED:
        app.add_middleware(
            SessionMiddleware,
            secret_key=get_config().secrets.SECRET_KEY,
            session_cookie=auth_cfg.SESSION_COOKIE_NAME,
            max_age=auth_cfg.SESSION_MAX_AGE_SECONDS,
            same_site=auth_cfg.SESSION_SAME_SITE,
            https_only=auth_cfg.SESSION_HTTPS_ONLY,
        )

    return app

def register_base_routes(app: FastAPI) -> None:
    from fastapi.responses import JSONResponse, PlainTextResponse
    from datetime import datetime
    @app.get(
        "/",
        summary="Resumen de configuración del backend",
        description="Estado, resumen de configuración y módulos activos.",
        response_class=JSONResponse,
    )
    def root():
        return {
            "status": "ONLINE",
            "config": get_config().NAME,
            "modules": len(app.routes),
            "now": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }

    @app.get(
        "/health",
        summary="Health endpoint",
        response_class=PlainTextResponse
    )
    def health_state(request: Request):
        get_logger().info(f"System ONLINE: {request.client}")
        return "OK"
    
    if get_config().server.DEBUG:
        @app.get(
            "/config"
        )
        def _get_config():
            return cfg
        
def _args_parse() -> dict:
    def _clean_none(d: dict) -> dict:
        return {
            k: _clean_none(v) if isinstance(v, dict) else v
            for k, v in d.items()
            if v is not None and v != []
        }
        
    parser = argparse.ArgumentParser(
        description="Process command line arguments.",
    )
    server = parser.add_argument_group("server")
    server.add_argument("-p", "--port", type=int, default=None)
    server.add_argument("-d", "--debug", action="store_true")
    server.add_argument("-H", "--host", type=str, default=None)
    logs = parser.add_argument_group("logs")
    logs.add_argument("-n", "--no-logs", action="store_true", default=False, help="Deshabilita el volcado a fichero de logs (stdout/stderr siguen).")
    runtime = parser.add_argument_group("runtime")
    runtime.add_argument("-R", "--restrict-modules", nargs="+", default=[], help="Lista blanca de módulos a registrar.")
    runtime.add_argument("-c", "--config", default="default")
    args = parser.parse_args()

    
    d = {
        "NAME": args.config,
        "server": {
            "HOST": args.host,
            "PORT": args.port,
            "DEBUG": args.debug,
            "RESTRICT_MODULES": args.restrict_modules
        },
        "logs": {
            "LOGS_DISABLE": args.no_logs,
        },
    }
    return {
        k: _clean_none(v) if isinstance(v, dict) else v
        for k, v in d.items()
        if v is not None and v != []
    }

def _print_startup_table(cfg: Config) -> None:
    from rich.table import Table
    from rich.panel import Panel
    from rich.console import Console
    
    f_enabled = lambda cond: "✓ Enabled" if cond else "✗ Not Enabled"
    console = Console()
    table = Table(title="⚙️  Configuración del Servidor", show_header=True, header_style="bold cyan")
    table.add_column("Parámetro", style="green")
    table.add_column("Valor",     style="yellow")

    table.add_row("URL",          f"http://{cfg.server.HOST}:{cfg.server.PORT}")
    table.add_row("Debug",       f_enabled (cfg.server.DEBUG))
    table.add_row("ConfigFile", str(cfg.CONFIG_FILE.absolute()))
    table.add_row(
        "Logs", # 
        f"{f_enabled(not cfg.logs.LOGS_DISABLE)} {f'({cfg.logs.LOGS_FILE})' if (not cfg.logs.LOGS_DISABLE) else ''}",
    )
    table.add_row("DatabaseType", get_config().database.DB_TYPE)
    table.add_row(
        "Auth",
        f_enabled(get_config().auth.ENABLED),
    )
    table.add_row(
        "OAuth",
        f_enabled(get_config().auth.OAUTH.ENABLED),
    )
    table.add_row(
        "Keycloak",
        f_enabled(get_config().auth.KEYCLOAK.ENABLED),
    )

    console.print(table)
    console.print(Panel(f"[bold green]Iniciando servidor {cfg.server.VERSION}[/bold green]", expand=False))

def _check_services() -> None:
    """Valida que los servicios críticos estén disponibles antes de arrancar."""
    try:
        pass  # e.g.: get_db_service().ping()
    except Exception as e:
        get_logger().critical(f"Error al inicializar servicios: {e}")
        raise e


if __name__ == "__main__":
    cli_cfg = _args_parse()
    config_name = cli_cfg.get('NAME')
    try:
        cfg = load_config(config_name)
        cfg = update_config(cli_cfg)
        # implicit loads with config
        load_logger(cfg.logs)
    except Exception as e:
        get_logger().critical(f"cannot load config file ({config_name}) ABORTANDO")
        exit(1)

    app = create_app("app", "descripción", cfg)
    register_base_routes(app)

    _print_startup_table(cfg)
    _check_services()
    uvicorn.run(
        app=app,
        host=cfg.server.HOST,
        port=cfg.server.PORT,
        log_config=None,
        reload=False,
    )
