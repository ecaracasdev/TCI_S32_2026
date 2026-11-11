import { Observable } from 'rxjs';

import { RepuestoDto } from '../repuestos/repuestos.models';

export abstract class ComprasService {

  abstract listar(): Observable<RepuestoDto[]>;

}