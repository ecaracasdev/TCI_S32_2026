import { baseEnvironment } from "./environment.base";

export const environment = {
  ...baseEnvironment,
  apiUrl: "http://localhost:5000",
  useMockData: false,
  production: false
};
