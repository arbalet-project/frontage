/* eslint-disable object-shorthand */
import { ServiceSchema } from 'moleculer';
import Config from './services/Config';

export default {
  name: Config.name,
  dependencies: [
  ],
  events: {
  },
} as ServiceSchema;
