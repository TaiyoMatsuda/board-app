<template>
  <div class="user">
    <h1>This is user page</h1>
    <BaseUser />
  </div>
</template>

<script>
import BaseUser from '@/components/User/BaseUser.vue'

export default {
  name: 'User',
  components: {
    BaseUser
  }
}
</script>
