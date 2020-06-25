import { Router } from "https://deno.land/x/oak/mod.ts";
import { getStatus } from "./controller/status.ts";

const router = new Router();

router
    .get('/status', getStatus);

export default router;