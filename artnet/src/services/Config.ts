import { config } from 'dotenv';
import { get } from 'env-var';

config();

const Config = {
  name: get('NAME').default('STATE').asString(),
  logLevel: get('LOGLEVEL')
    .default('info')
    .asEnum(['info', 'fatal', 'error', 'warn', 'debug', 'trace']),
  frontage: {
    width: get('WIDTH').default(19).asIntPositive(),
    height: get('HEIGHT').default(4).asIntPositive(),
  },
};

export default Config;
