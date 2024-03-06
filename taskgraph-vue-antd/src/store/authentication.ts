import { defineStore } from "pinia";
import { type RemovableRef, useStorage } from "@vueuse/core";
import { computed } from "vue";

export enum TokenStatus {
  Validated = "Validated",
  Invalid = "Invalid",
  ToExpire = "To Expire",
  Expired = "Expired",
  Unknown = "Unknown",
}

export interface TokenState {
  jwt: string;
  type: string;
  created: number | null; // timestamp in miliseconds, since JSON cannot serialize Date()
  expire: number | null; // timestamp in miliseconds, since JSON cannot serialize Date()
  status: TokenStatus;
}

export const useTokenStore = defineStore("token", () => {
  const token: RemovableRef<TokenState> = useStorage(
    "taskgraph-token-local-storage",
    {
      jwt: "",
      type: "",
      created: null,
      expire: null,
      status: TokenStatus.Unknown,
    }
  );

  const created_formatted = computed(() => {
    if (token.value.created) {
      const date_created = new Date(token.value.created);
      return date_created.toString();
    } else {
      return "-";
    }
  });

  const expire_formatted = computed(() => {
    if (token.value.expire) {
      const date_expire = new Date(token.value.expire);
      return date_expire.toString();
    } else {
      return "-";
    }
  });

  return { token, created_formatted, expire_formatted };
});
