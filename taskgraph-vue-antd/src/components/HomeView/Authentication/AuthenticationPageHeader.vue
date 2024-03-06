<template>
  <a-page-header
    class="auth-page-header"
    style="border: 1px solid rgb(235, 237, 240)"
    title="Auth Tool"
    sub-title="for oauth2.0"
  >
    <template #extra>
      <a-button key="2" type="primary" @click="handleValidate">
        Validate Token
      </a-button>
      <a-button key="1" danger @click="handleDiscard"> Discard Token </a-button>
    </template>
    <a-descriptions
      size="small"
      :column="{ xxl: 4, xl: 3, lg: 3, md: 2, sm: 1, xs: 1 }"
    >
      <a-descriptions-item label="Token Status">
        <div class="token-status-desc-box">
          <CloseCircleTwoTone
            two-tone-color="#ff0000"
            v-if="tokenStore.token.status == TokenStatus.Invalid"
          />
          <CloseCircleTwoTone
            two-tone-color="#ff0000"
            v-else-if="tokenStore.token.status == TokenStatus.Expired"
          />
          <WarningTwoTone
            two-tone-color="#eeaa00"
            v-else-if="tokenStore.token.status == TokenStatus.ToExpire"
          />
          <WarningTwoTone
            two-tone-color="#eeaa00"
            v-else-if="tokenStore.token.status == TokenStatus.Unknown"
          />
          <CheckCircleTwoTone
            two-tone-color="#52c41a"
            v-else-if="tokenStore.token.status == TokenStatus.Validated"
          />
          {{ tokenStore.token.status }}
        </div>
      </a-descriptions-item>
      <a-descriptions-item label="Last Login">
        {{ tokenStore.created_formatted }}
      </a-descriptions-item>
      <a-descriptions-item label="Expiration">
        {{ tokenStore.expire_formatted }}
      </a-descriptions-item>
      <a-descriptions-item label="Remote">
        {{ connInfoStore.restful_endpoint }}
      </a-descriptions-item>
      <a-descriptions-item label="Scheme">
        {{ tokenStore.token.type }}
      </a-descriptions-item>
      <a-descriptions-item label="Encryption">
        <div class="encryption-desc-box">
          <CloseCircleTwoTone
            two-tone-color="#ff0000"
            v-if="encryption_status == EncryptionStatus.UnsafeAll"
          />
          <WarningTwoTone
            two-tone-color="#eeaa00"
            v-else-if="encryption_status == EncryptionStatus.UnsafeAPI"
          />
          <WarningTwoTone
            two-tone-color="#eeaa00"
            v-else-if="encryption_status == EncryptionStatus.UnsafeApp"
          />
          <CheckCircleTwoTone
            two-tone-color="#52c41a"
            v-else-if="encryption_status == EncryptionStatus.Everywhere"
          />
          {{ encryption_status }}
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
import { computed } from "vue";
import {
  WarningTwoTone,
  CheckCircleTwoTone,
  CloseCircleTwoTone,
} from "@ant-design/icons-vue";
import { useConnectionInfoStore } from "@/store/connection";
import { useTokenStore, TokenStatus } from "@/store/authentication";

const connInfoStore = useConnectionInfoStore();
const tokenStore = useTokenStore();

const user_agent = window.navigator.userAgent;
const user_agent_short =
  user_agent.length < 50
    ? user_agent
    : user_agent.slice(0, 25) + " ... " + user_agent.slice(-25);

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

enum EncryptionStatus {
  Everywhere = "Everywhere",
  UnsafeAPI = "Unsafe API",
  UnsafeApp = "Unsafe Frontend",
  UnsafeAll = "Unsafe",
}

function isEverythingEncrypted(api_origin: string): EncryptionStatus {
  let api_safe = false;
  if (api_origin.startsWith("https")) {
    api_safe = true;
  }
  let app_safe = false;
  if (location.protocol === "https") {
    app_safe = true;
  }
  if (api_safe && app_safe) return EncryptionStatus.Everywhere;
  if (api_safe && !app_safe) return EncryptionStatus.UnsafeApp;
  if (!api_safe && app_safe) return EncryptionStatus.UnsafeAPI;
  return EncryptionStatus.UnsafeAll;
}

const encryption_status = computed(() =>
  isEverythingEncrypted(connInfoStore.restful_endpoint)
);

const handleValidate = async () => {
  // console.log("Validating current token: ", toRaw(tokenStore.token));
  // check for expiration
  const tnow = new Date().getTime();
  if (tokenStore.token.expire) {
    if (tokenStore.token.expire < tnow) {
      tokenStore.token.status = TokenStatus.Expired;
      return;
    }
  }
  // before fetching reset displayed status
  tokenStore.token.status = TokenStatus.Unknown;
  try {
    // try to fetch some authorized api to test if token is valid
    const response = await fetch(connInfoStore.restful_endpoint + "projects", {
      method: "GET",
      body: null, // string or object
      headers: {
        accept: "application/json",
        Authorization: tokenStore.token.type + " " + tokenStore.token.jwt,
      },
    });
    if (response?.ok) {
      const response_json = await response.json();
      // success, token is valid. Check for expiration
      console.log("Seems token is valid, got response: ", response_json);
      if (tokenStore.token.expire) {
        const tdelta = tokenStore.token.expire - tnow;
        if (tdelta < 3600000) {
          // expiring in a hour
          tokenStore.token.status = TokenStatus.ToExpire;
          return;
        }
      }
      tokenStore.token.status = TokenStatus.Validated;
    } else {
      // Got abnormal response code.
      console.log(
        "Server reported an issue, HTTP Response Code: ",
        response?.status
      );
      tokenStore.token.status = TokenStatus.Invalid;
    }
  } catch (error) {
    if (error instanceof SyntaxError) {
      // Got abnormal data.
      console.log("Remoted returned non-json data.");
    } else if (error instanceof TypeError) {
      // Service down.
      console.log("Fetching remote resource failed, probably disconnected");
      console.log(error);
    } else {
      // Other errors, probably user canceled request or network change.
      console.log("Unexpected error", error);
    }
  }
};

function handleDiscard() {
  // user wants to discard current token.
  // clear saved token, and flag token status as invalid.
  // useStorage hooks will automatically delete localStorage.
  tokenStore.token.jwt = "";
  tokenStore.token.type = "";
  tokenStore.token.status = TokenStatus.Invalid;
  tokenStore.token.created = null;
  tokenStore.token.expire = null;
}
</script>

<style scoped>
.auth-page-header :deep(tr:last-child td) {
  padding-bottom: 0;
}
</style>
