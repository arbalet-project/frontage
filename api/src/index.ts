import { ServiceBroker } from "moleculer";

import BrokerConfig from "./BrokerConfig";
import Service from "./Service";

const broker = new ServiceBroker(BrokerConfig);

broker.createService(Service);

broker.start().catch((err) => {
  broker.logger.error(err);
});
