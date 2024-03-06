import { createApp } from "vue";
import Antd from "ant-design-vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import "ant-design-vue/dist/reset.css";

const app = createApp(App);
app.use(store);
app.use(router);
app.use(Antd);
app.mount("#app");
