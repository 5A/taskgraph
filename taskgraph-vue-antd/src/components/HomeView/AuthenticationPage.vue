<template>
  <a-breadcrumb style="margin: 16px 0">
    <a-breadcrumb-item>TaskGraph</a-breadcrumb-item>
    <a-breadcrumb-item>Workbench</a-breadcrumb-item>
    <a-breadcrumb-item>Authentication</a-breadcrumb-item>
  </a-breadcrumb>
  <AuthenticationPageHeader />
  <br />
  <AuthenticationContent />
</template>

<script lang="ts" setup>
import AuthenticationPageHeader from "./Authentication/AuthenticationPageHeader.vue";
import AuthenticationContent from "./Authentication/AuthenticationContent.vue";
</script>
