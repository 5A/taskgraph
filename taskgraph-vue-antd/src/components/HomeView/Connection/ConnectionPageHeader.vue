<template>
  <a-page-header
    class="conn-page-header"
    style="border: 1px solid rgb(235, 237, 240)"
    title="Connection Settings"
    sub-title="RESTful API Config"
  >
    <template #extra>
      <label>
        <input
          ref="import_file_input"
          v-on:change="handleFileSelected()"
          type="file"
          accept=".json"
          style="display: none"
        />
        <a-button key="1" type="primary" @click="import_file_input?.click()">
          <ImportOutlined />
          Import
        </a-button>
      </label>
      <a-button key="2" @click="handleExport"
        ><ExportOutlined />Export</a-button
      >
    </template>
    <a-descriptions
      size="small"
      :column="{ xxl: 4, xl: 3, lg: 3, md: 2, sm: 1, xs: 1 }"
    >
      <a-descriptions-item label="RESTful">
        <div class="restful-status-desc-box">
          <CloseCircleTwoTone
            two-tone-color="#ff0000"
            v-if="connStatusState.restful == RestfulStatus.Offline"
          />
          <CloseCircleTwoTone
            two-tone-color="#ff0000"
            v-else-if="connStatusState.restful == RestfulStatus.Error"
          />
          <WarningTwoTone
            two-tone-color="#eeaa00"
            v-else-if="connStatusState.restful == RestfulStatus.Unknown"
          />
          <CheckCircleTwoTone
            two-tone-color="#0000ff"
            v-else-if="connStatusState.restful == RestfulStatus.Online"
          />
          {{ connStatusState.restful }}
        </div>
      </a-descriptions-item>
      <a-descriptions-item label="WebSocket">
        <div class="ws-status-desc-box">
          <CloseCircleTwoTone
            two-tone-color="#ff0000"
            v-if="test_websocket_status == WebSocketStatus.Error"
          />
          <WarningTwoTone
            two-tone-color="#eeaa00"
            v-else-if="test_websocket_status == WebSocketStatus.Unknown"
          />
          <CheckCircleTwoTone
            two-tone-color="#0000ff"
            v-else-if="test_websocket_status == WebSocketStatus.Ready"
          />
          <CheckCircleTwoTone
            two-tone-color="#52c41a"
            v-else-if="test_websocket_status == WebSocketStatus.Connected"
          />
          {{ test_websocket_status }}
        </div>
      </a-descriptions-item>
      <a-descriptions-item label="gRPC">
        <div class="grpc-status-desc-box">
          <CloseCircleTwoTone
            two-tone-color="#ff0000"
            v-if="connStatusState.grpc == GRPCStatus.Offline"
          />
          <WarningTwoTone
            two-tone-color="#eeaa00"
            v-else-if="connStatusState.grpc == GRPCStatus.Unknown"
          />
          <CheckCircleTwoTone
            two-tone-color="#0000ff"
            v-else-if="connStatusState.grpc == GRPCStatus.Online"
          />
          {{ connStatusState.grpc }}
        </div>
      </a-descriptions-item>
      <a-descriptions-item label="Allow localStorage">
        {{ localstorage_enabled }}
      </a-descriptions-item>
      <a-descriptions-item label="Client">
        <a-tooltip>
          <template #title>{{ user_agent }}</template>
          {{ user_agent_short }}
        </a-tooltip>
      </a-descriptions-item>
    </a-descriptions>
  </a-page-header>
</template>

<script lang="ts" setup>
import { toRaw, ref, computed } from "vue";
import { storeToRefs } from "pinia";
import {
  WarningTwoTone,
  CheckCircleTwoTone,
  CloseCircleTwoTone,
  ImportOutlined,
  ExportOutlined,
} from "@ant-design/icons-vue";
import { message } from "ant-design-vue";

import {
  useConnectionStatusStore,
  useConnectionInfoStore,
  type ConnectionInfoState,
  RestfulStatus,
  WebSocketStatus,
  GRPCStatus,
} from "@/store/connection";

// Import and Export connection info.
const connInfoStore = useConnectionInfoStore();

// #region import
// define function and callback for Import button on the page header title #extra

// create ref for file input element so that a button can trigger the hidden input.
const import_file_input = ref<HTMLInputElement | null>(null);

// TypeScript does not have data validation capabilities, so we cannot easily validate user input against our model...
// The workaround here is to try to patch user input directly, and if the patch fails due to some error, we simply
//  clear all fields in the model and alerts the user to re-input data.
function handleImport(imported: ConnectionInfoState) {
  try {
    connInfoStore.$patch({ connInfoState: imported });
  } catch (error) {
    console.log(
      "Patching to current state failed! Imported state is ",
      imported,
      "Error is: ",
      error
    );
    connInfoStore.$reset();
    message.error(
      "Patching to current state failed, please check your input and try again."
    );
  }
}

// When a file is selected, try to parse the selected file.
const handleFileSelected = async () => {
  // check if the file input element has loaded, if loaded, get its files.
  let files = import_file_input.value?.files;
  // if files are not empty, load first element as file blob because we didn't allow multiple file selection.
  let file = files ? files[0] : null;
  // if file selection is succesful, try to read filename and load blob content as text.
  let filename = file?.name;
  // the blob.text() method will not throw error even for non-text files so no need to catch here.
  let import_text = file ? await file.text() : null;
  try {
    // if file loaded successfully, parse it as json.
    let parsed = import_text ? JSON.parse(import_text) : null;
    console.log(parsed);
    if (parsed) {
      // try to patch current state if read is successful.
      handleImport(parsed);
      message.info(`Imported ${filename} successfully.`);
    }
  } catch (SyntaxError) {
    // parse failed, don't patch anything and alert the user.
    message.error(
      "Importing " +
        filename +
        " failed because it is not a valid JSON config file."
    );
  }
};
// #endregion

// #region export
// define function and callback for Export button on the page header title #extra

// export an object as json and trigger download
// Copy & Pasted from https://stackoverflow.com/a/30800715
function downloadObjectAsJson(exportObj: object, exportName: string) {
  var dataStr =
    "data:text/json;charset=utf-8," +
    encodeURIComponent(JSON.stringify(exportObj));
  var downloadAnchorNode = document.createElement("a");
  downloadAnchorNode.setAttribute("href", dataStr);
  downloadAnchorNode.setAttribute("download", exportName + ".json");
  document.body.appendChild(downloadAnchorNode); // required for firefox
  downloadAnchorNode.click();
  downloadAnchorNode.remove();
}

function handleExport() {
  downloadObjectAsJson(toRaw(connInfoStore.connInfoState), "ConnectionConfig");
}
// #endregion

// #region status_description

// First row of page header description is current connection status.
// The connection status is saved in connnection status store's state.
// The connection status is updated in other modules when connection status is tested.
const connStatusStore = useConnectionStatusStore();
const { connStatusState } = storeToRefs(connStatusStore);
// Check status of our testing websocket.
const test_websocket_status = computed(
  () =>
    // When device supports multiple ws endpoints, this status should be synced with test-websocket only
    // but when there's only one ws endpoint, we directly tie this to the operating websocket
    // to make it more intuitive for the user.
    // connStatusState.value.websockets.get("test-websocket") ??
    // WebSocketStatus.Unknown
    connStatusState.value.websockets.get("websocket-taskgraph") ??
    WebSocketStatus.Unknown
);

// Second row of page header includes user browser configs.
// If localStorage is available, input connection info is saved and the next time the user opens app, there's no need
//  to re-input or import. For some browsers, it is possible that the user can disable localStorage, causing the fields
//  to be cleared every time the session ends. And this description hints the user if localStorage is disallowed.
function isLocalStorageAvailable() {
  let test = "test";
  try {
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch (e) {
    return false;
  }
}
const localstorage_enabled = isLocalStorageAvailable();
// User agent can be used to help identify the source of API access.
// UAs are in general quite long, so it is necessary to truncate the string into shorter versions to display.
// A Tooltip is used to display the full UA string when mouse hover or touch.
const user_agent = window.navigator.userAgent;
const user_agent_short =
  user_agent.length < 50
    ? user_agent
    : user_agent.slice(0, 25) + " ... " + user_agent.slice(-25);

// #endregion
</script>

<style scoped>
.conn-page-header :deep(tr:last-child td) {
  padding-bottom: 0;
}
</style>
