import { config } from "./config.js";
import { createApp } from "./app.js";

const app = createApp();

app.listen(config.PORT, () => {
  console.log(`${config.APP_NAME} listening on port ${config.PORT}`);
});
