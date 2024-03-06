<template>
  <a-breadcrumb style="margin: 16px 0">
    <a-breadcrumb-item>TaskGraph</a-breadcrumb-item>
    <a-breadcrumb-item>Workbench</a-breadcrumb-item>
    <a-breadcrumb-item>Connection</a-breadcrumb-item>
  </a-breadcrumb>
  <ConnectionPageHeader />
  <br />
  <ConnectionCentent />
</template>

<script lang="ts" setup>
import ConnectionPageHeader from "./Connection/ConnectionPageHeader.vue";
import ConnectionCentent from "./Connection/ConnectionContent.vue";
</script>
