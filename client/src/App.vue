<template>
  <div id="app" class="mb-6">
    <Header/>
    <router-view/>
    <confirm-modal></confirm-modal>
  </div>
</template>

<script>
import Header from '@/views/Header.vue'
import ConfirmModal from '@/components/modals/ConfirmModal'

export default {
  components: {
    Header,
    ConfirmModal
  }
}

</script>

<style lang="scss">
@import "~bulma";

.button.is-link.my-disabled-button {
  opacity: 0.5;
  background-color: #485fc7;
  border-color: #485fc7;
  box-shadow: none;
}

.my-disbaled-field {
  -webkit-text-fill-color: #7a7a7a;
  opacity: 1; /* required on iOS */
}
</style>
