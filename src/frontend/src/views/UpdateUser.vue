<template>
  <div class="user">
    <h1>This is user page</h1>
    <p>ユーザID:{{ user.id }}</p>
    <p>ユーザ名:{{ user.first_name }}</p>
    <p>ユーザ姓:{{ user.family_name }}</p>
    <p>紹介文:{{ user.introduction }}</p>
    <p>ガイドフラグ:{{ user.is_guide }}</p>
    <p>ユーザアイコン:{{ user.icon }}</p>
    <p>email:{{ email }}</p>
    <BaseUser v-on:parentGetUser="getUser"></BaseUser>
    <UserEmail v-on:parentGetUserEmail="getUserEmail"></UserEmail>
    <router-link to="/update_password">Edit password</router-link>
  </div>
</template>

<script>
import BaseUser from '@/components/User/BaseUser.vue'
import UserEmail from '@/components/User/UserEmail.vue'

export default {
  name: 'UpdateUser',
  data() {
    return {
      user: [],
      email: []
    }
  },
  components: {
    BaseUser,
    UserEmail
  },
  methods: {
    getUser: function(user) {
      this.user = user;
    },
    getUserEmail: function(email) {
      this.email = email;
    }
  }
}
</script>
