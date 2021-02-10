<template>
  <div class="user">
    <h1>This is update user page</h1>
    <BaseUser />
    <UserEmail />
    <router-link to="/update_password">Edit password</router-link>
  </div>
</template>

<script>
import BaseUser from '@/components/User/BaseUser.vue'
import UserEmail from '@/components/User/UserEmail.vue'

export default {
  name: 'UpdateUser',
  components: {
    BaseUser,
    UserEmail
  },
}
</script>
