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
      :model="formState"
      name="basic"
      layout="horizontal"
      :label-col="{ span: 8 }"
      :wrapper-col="{ span: 16 }"
      autocomplete="off"
      @finish="onFinish"
      @finishFailed="onFinishFailed"
    >
      <a-form-item
        label="Username"
        name="username"
        :rules="[
          {
            required: true,
            message: 'Username cannot be empty.',
          },
        ]"
      >
        <a-input v-model:value="formState.username" />
      </a-form-item>

      <a-form-item
        label="Password"
        name="password"
        :rules="[
          {
            required: true,
            message: 'Password cannot be empty.',
          },
        ]"
      >
        <a-input-password v-model:value="formState.password" />
      </a-form-item>

      <a-form-item name="remember" :wrapper-col="{ offset: 8, span: 16 }">
        <a-checkbox v-model:checked="formState.remember">
          Use this token to authenticate current application
        </a-checkbox>
      </a-form-item>

      <a-form-item :wrapper-col="{ offset: 8, span: 16 }">
        <a-button type="primary" html-type="submit">Request New Token</a-button>
      </a-form-item>
    </a-form>
    <a-card title="JSON Web Token">
      <pre>{{ token_temporary }}</pre>
    </a-card>
  </a-layout-content>
</template>

<script lang="ts" setup>
import { reactive, ref } from "vue";
import { jwtDecode } from "jwt-decode";
import { TokenStatus, useTokenStore } from "@/store/authentication";
import { useConnectionInfoStore } from "@/store/connection";

const token_temporary = ref<string>("");
const tokenStore = useTokenStore();
const connInfoStore = useConnectionInfoStore();

interface FormState {
  username: string;
  password: string;
  remember: boolean;
}

const formState = reactive<FormState>({
  username: "",
  password: "",
  remember: true,
});

const onFinish = async (values: FormState) => {
  tokenStore.token.status = TokenStatus.Unknown;
  // OAuth2 requires that username and password be passed as form data, not JSON.
  const formData = new FormData();
  formData.append("username", values.username);
  formData.append("password", values.password);
  try {
    const response = await fetch(connInfoStore.restful_endpoint + "token", {
      method: "POST",
      body: formData,
    });
    if (response?.ok) {
      const response_json = await response.json();
      if (values.remember) handleAuthSuccess(response_json);
      token_temporary.value = response_json.access_token;
    } else {
      // Got abnormal response code.
      console.log(
        "Server reported an issue, HTTP Response Code: ",
        response?.status
      );
      handleAuthFailure();
    }
  } catch (error) {
    if (error instanceof SyntaxError) {
      // Got abnormal data.
      console.log("Remoted returned non-json data.");
    } else if (error instanceof TypeError) {
      // Service down.
      console.log("Fetching remote resource failed, probably disconnected");
    } else {
      // Other errors, probably user canceled request or network change.
      console.log("Unexpected error", error);
    }
    handleAuthFailure();
  }
};

const onFinishFailed = () => {
  console.log("Login form validation failed, check yout input.");
};

interface AuthResponse {
  access_token: string;
  token_type: string;
}

function handleAuthSuccess(response_json: AuthResponse) {
  // auth success, save token for later use, and flag token status as valid.
  tokenStore.token.jwt = response_json.access_token;
  tokenStore.token.type = response_json.token_type;
  tokenStore.token.status = TokenStatus.Validated;
  const tnow = new Date();
  tokenStore.token.created = tnow.getTime();
  // get expiration time info from decode jwt.
  const decoded_jwt = jwtDecode(response_json.access_token);
  if (decoded_jwt.exp) {
    tokenStore.token.expire = decoded_jwt.exp * 1000; // seconds to miliseconds
  }
}

function handleAuthFailure() {
  // auth failure, clear saved token, and flag token status as invalid.
  tokenStore.token.jwt = "";
  tokenStore.token.type = "";
  tokenStore.token.status = TokenStatus.Invalid;
  tokenStore.token.created = null;
  tokenStore.token.expire = null;
}
</script>
