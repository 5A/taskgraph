<template>
  <a-layout-content
    :style="{
      background: '#fff',
      padding: '24px',
      margin: 0,
      minHeight: '280px',
    }"
  >
    <a-form
      :model="connInfoState"
      :label-col="labelCol"
      :wrapper-col="wrapperCol"
    >
      <a-form-item label="RESTful API Origin">
        <a-input-group compact>
          <a-select
            v-model:value="connInfoState.restful.protocol"
            style="width: 100px"
            :disabled="disable_restful"
          >
            <a-select-option value="http://">http://</a-select-option>
            <a-select-option value="https://">https://</a-select-option>
          </a-select>
          <a-input
            v-model:value="connInfoState.restful.host"
            style="width: calc(100% - 180px)"
            placeholder="app.taskgraph.org"
            :disabled="disable_restful"
          />
          <a-input-number
            v-model:value="connInfoState.restful.port"
            style="width: 80px"
            placeholder="port"
            :disabeld="disable_restful"
          />
        </a-input-group>
      </a-form-item>
      <a-form-item label="API Endpoint">
        <a-input-group compact>
          <a-input
            v-model:value="connInfoState.restful.endpoint"
            style="width: calc(100% - 60px)"
            placeholder="/"
            :disabled="disable_restful"
          />
          <a-button
            type="primary"
            style="width: 60px"
            @click="onTestRestful"
            :disabled="disable_restful"
          >
            Test
          </a-button>
        </a-input-group>
      </a-form-item>
      <a-form-item label="WebSocket API Origin">
        <a-input-group compact>
          <a-select
            v-model:value="connInfoState.websocket.protocol"
            style="width: 100px"
            :disabled="disable_websocket"
          >
            <a-select-option value="ws://">ws://</a-select-option>
            <a-select-option value="wss://">wss://</a-select-option>
          </a-select>
          <a-input
            v-model:value="connInfoState.websocket.host"
            style="width: calc(100% - 180px)"
            placeholder="app.taskgraph.org"
            :disabled="disable_websocket"
          />
          <a-input-number
            v-model:value="connInfoState.websocket.port"
            style="width: 80px"
            placeholder="port"
            :disabled="disable_websocket"
          />
        </a-input-group>
      </a-form-item>
      <a-form-item label="API Endpoint">
        <a-input-group compact>
          <a-input
            v-model:value="connInfoState.websocket.endpoint"
            style="width: calc(100% - 60px)"
            placeholder="/ws"
            :disabled="disable_websocket"
          />
          <a-button
            type="primary"
            style="width: 60px"
            @click="onTestWebsocket"
            :disabled="disable_websocket"
          >
            Test
          </a-button>
        </a-input-group>
      </a-form-item>
      <a-form-item label="gRPC API Origin">
        <a-input-group compact>
          <a-select
            v-model:value="connInfoState.grpc.protocol"
            style="width: 100px"
            :disabled="disable_grpc"
          >
            <a-select-option value="grpc://">grpc://</a-select-option>
          </a-select>
          <a-input
            v-model:value="connInfoState.grpc.host"
            style="width: calc(100% - 240px)"
            placeholder="app.taskgraph.org"
            :disabled="disable_grpc"
          />
          <a-input-number
            v-model:value="connInfoState.grpc.port"
            style="width: 80px"
            placeholder="port"
            :disabled="disable_grpc"
          />
          <a-button
            type="primary"
            style="width: 60px"
            :disabled="disable_grpc"
            @click="onTestGrpc"
            >Test</a-button
          >
        </a-input-group>
      </a-form-item>
    </a-form>
  </a-layout-content>
</template>

<script lang="ts" setup>
import { ref, toRaw } from "vue";
import { storeToRefs } from "pinia";
import {
  RestfulStatus,
  WebSocketStatus,
  useConnectionInfoStore,
  useConnectionStatusStore,
  useWebSocketManagerStore,
} from "@/store/connection";

const connInfoStore = useConnectionInfoStore();
const { connInfoState, restful_endpoint, websocket_endpoint } =
  storeToRefs(connInfoStore);
const connStatusStore = useConnectionStatusStore();
const webSocketManagerStore = useWebSocketManagerStore();
const disable_restful = ref<boolean>(false);
const disable_websocket = ref<boolean>(false);
const disable_grpc = ref<boolean>(true);

const onTestRestful = async () => {
  console.log(
    "Testing RESTful Availability with config: ",
    toRaw(connInfoState.value.restful)
  );
  console.log("Target RESTful origin: ", restful_endpoint.value);
  // before fetching reset displayed status
  connStatusStore.connStatusState.restful = RestfulStatus.Unknown;
  try {
    const response = await fetch(restful_endpoint.value, {
      method: "GET",
      body: null, // string or object
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (response?.ok) {
      const response_json = await response.json();
      // success, modify state to online.
      console.log("RESTful online, got response: ", response_json);
      connStatusStore.connStatusState.restful = RestfulStatus.Online;
    } else {
      // Got abnormal response code.
      console.log(
        "Server reported an issue, HTTP Response Code: ",
        response?.status
      );
      connStatusStore.connStatusState.restful = RestfulStatus.Error;
    }
  } catch (error) {
    if (error instanceof SyntaxError) {
      // Got abnormal data.
      console.log("Remoted returned non-json data.");
      connStatusStore.connStatusState.restful = RestfulStatus.Error;
    } else if (error instanceof TypeError) {
      // Service down.
      console.log("Fetching remote resource failed, probably disconnected");
      connStatusStore.connStatusState.restful = RestfulStatus.Offline;
    } else {
      // Other errors, probably user canceled request or network change.
      console.log("Unexpected error", error);
      connStatusStore.connStatusState.restful = RestfulStatus.Unknown;
    }
  }
};

const onTestWebsocket = () => {
  // When device supports multiple ws endpoints, this status should be synced with test-websocket only
  // but when there's only one ws endpoint, we directly tie this to the operating websocket
  // to make it more intuitive for the user.
  // const wsid = "test-websocket";
  const wsid = "websocket-taskgraph";
  const target_url = websocket_endpoint.value;
  console.log(
    "Testing WebSocket Availability with config: ",
    toRaw(connInfoState.value.websocket)
  );
  console.log("Target WebSocket origin: ", target_url);
  // before connecting to websocket, reset displayed status
  connStatusStore.connStatusState.websockets.set(wsid, WebSocketStatus.Unknown);
  try {
    // create a temporary websocket to test websocket
    webSocketManagerStore.createNewWebSocket({
      wsid: wsid,
      url: target_url,
      on_open: function (this, ev) {
        console.log("websocket open", ev);
        connStatusStore.connStatusState.websockets.set(
          wsid,
          WebSocketStatus.Connected
        );
        this.close();
      },
      on_close: function (this, ev) {
        console.log("websocket closed", ev);
        if (ev.wasClean) {
          connStatusStore.connStatusState.websockets.set(
            wsid,
            WebSocketStatus.Ready
          );
        } else {
          console.log("Websocket closed but not clean!");
          connStatusStore.connStatusState.websockets.set(
            wsid,
            WebSocketStatus.Error
          );
        }
      },
      on_error: function (this, ev) {
        console.log("websocket error", ev);
        connStatusStore.connStatusState.websockets.set(
          wsid,
          WebSocketStatus.Error
        );
      },
    });
  } catch (error) {
    console.log(error);
  }
};

const onTestGrpc = () => {
  console.log(
    "Testing gRPC Availability with config: ",
    toRaw(connInfoState.value.grpc)
  );
};

const labelCol = { style: { width: "150px" } };
const wrapperCol = { span: 14 };
</script>

<style scoped>
.param-input {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
  white-space: nowrap;
}
</style>
