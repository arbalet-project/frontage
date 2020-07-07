import { config } from 'dotenv';
import { get } from 'env-var';

config();

const Config = {
  name: get('NAME').default('STATE').asString(),
  logLevel: get('LOGLEVEL')
    .default('info')
    .asEnum(['info', 'fatal', 'error', 'warn', 'debug', 'trace'])
};

export default Config;
