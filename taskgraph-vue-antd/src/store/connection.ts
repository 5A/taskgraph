import { defineStore } from "pinia";
import { type RemovableRef, useStorage } from "@vueuse/core";
import { type UnwrapRef, computed, reactive } from "vue";

export interface ConnectionInfoState {
  restful: {
    protocol: string;
    host: string;
    port: number;
    endpoint: string;
  };
  websocket: {
    protocol: string;
    host: string;
    port: number;
    endpoint: string;
  };
  grpc: {
    protocol: string;
    host: string;
    port: number;
  };
}

export const useConnectionInfoStore = defineStore(
  "taskgraph-connection-info",
  () => {
    const connInfoState: RemovableRef<ConnectionInfoState> = useStorage(
      "taskgraph-connection-info-local-storage",
      {
        restful: {
          protocol: "http://",
          host: "",
          port: 8000,
          endpoint: "/",
        },
        websocket: {
          protocol: "ws://",
          host: "",
          port: 8000,
          endpoint: "/ws",
        },
        grpc: {
          protocol: "grpc://",
          host: "",
          port: 9000,
        },
      }
    );

    const restful_endpoint = computed(() => {
      return (
        connInfoState.value.restful.protocol +
        connInfoState.value.restful.host +
        ":" +
        connInfoState.value.restful.port +
        connInfoState.value.restful.endpoint
      );
    });

    const websocket_endpoint = computed(() => {
      return (
        connInfoState.value.websocket.protocol +
        connInfoState.value.websocket.host +
        ":" +
        connInfoState.value.websocket.port +
        connInfoState.value.websocket.endpoint
      );
    });

    return { connInfoState, restful_endpoint, websocket_endpoint };
  }
);

export enum RestfulStatus {
  // Online: service useable. Note that this does not check if the user has access or the server is functioning as
  //         expected. It only tries to GET the server to see if it is alive.
  Online = "Online",
  Offline = "Offline", // no response from server, server is probably down or unreachable.
  Error = "Error", // got response from server, but response code is not 200 OK, or response content is not json.
  Unknown = "Unknown", // status not probed yet or probe is in progress.
}

export enum WebSocketStatus {
  // Note that there's no Offline status here, because it is hard to distinguish between service offline or other ws
  //  errors. All we get from the WebSocket browser API is an Error event, and we can't tell if the event is triggered
  //  by some server side settings returned intentionally, or a malfunctioning server.
  // Also the ws APIs always closes the connection immediately if some error happens, so error basically means offline.
  Connected = "Connected", // connection active
  Ready = "Ready", // service useable, but no connection is active
  Error = "Error", // server responsed error or websocket connection is abnormal.
  Unknown = "Unknown", // status not probed yet or probe is in progress.
}

export enum GRPCStatus {
  Online = "Online",
  Offline = "Offline",
  Unknown = "Unknown",
}

// since we can establish multiple connections to different websocket endpoints for different purposes, we have to save
// multiple status to represent each one of the connections.
export interface ConnectionStatusState {
  restful: RestfulStatus;
  websockets: Map<string, WebSocketStatus>;
  grpc: GRPCStatus;
}

export const useConnectionStatusStore = defineStore(
  "taskgraph-connection-status",
  () => {
    const connStatusState: UnwrapRef<ConnectionStatusState> = reactive({
      restful: RestfulStatus.Unknown,
      websockets: new Map(),
      grpc: GRPCStatus.Unknown,
    });
    return { connStatusState };
  }
);

export interface WebSocketManagerState {
  websockets: Map<string, WebSocket>;
}

export const useWebSocketManagerStore = defineStore(
  "taskgraph-websocket-manager",
  () => {
    // a place to store all existing websockets.
    // whoever stores its websocket here can access the websocket by specifying a wsid string (the key).
    // if a websocket is closed, it is not removed from the map, because other states may still rely on some state of
    //  that websocket, for example some displaying element reading the websocket's readyState property.
    // when a new websocket is created for the same id, it is overwritten.
    const webSocketManagerState: UnwrapRef<WebSocketManagerState> = reactive({
      websockets: new Map(),
    });

    // when adding new websockets to store, this convenient function can be used.
    function createNewWebSocket({
      wsid,
      url,
      on_message,
      on_open,
      on_close,
      on_error,
    }: {
      wsid: string;
      url: string;
      on_message?: (this: WebSocket, ev: MessageEvent) => void;
      on_open?: (this: WebSocket, ev: Event) => void;
      on_close?: (this: WebSocket, ev: CloseEvent) => void;
      on_error?: (this: WebSocket, ev: Event) => void;
    }) {
      // creates WebSocket object according to url
      const ws = new WebSocket(url);
      // bind event listeners if given
      if (on_open) ws.onopen = on_open;
      if (on_close) ws.onclose = on_close;
      if (on_message) ws.onmessage = on_message;
      if (on_error) ws.onerror = on_error;
      // add newly created websocket to our store state, so that it is saved for later use.
      webSocketManagerState.websockets.set(wsid, ws);
    }

    return { webSocketManagerState, createNewWebSocket };
  }
);
