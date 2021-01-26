<template>
  <div class="user">
    <h1>This is user page</h1>
    <router-link :to="{ name: 'UpdateUser', query: { id: user.id}}">
      edit
    </router-link>
    <p>ユーザID:{{ user.id }}</p>
    <p>ユーザ名:{{ user.first_name }}</p>
    <p>ユーザ姓:{{ user.family_name }}</p>
    <p>紹介文:{{ user.introduction }}</p>
    <p>ガイドフラグ:{{ user.is_guide }}</p>
    <p>ユーザアイコン:{{ user.icon }}</p>
    <BaseUser v-on:parentGetUser="getUser"></BaseUser>
    <EventList />
  </div>
</template>

<script>
import BaseUser from '@/components/User/BaseUser.vue'
import EventList from '@/components/Event/EventList.vue'

export default {
  name: 'User',
  data() {
    return {
      user: []
    }
  },
  components: {
    BaseUser,
    EventList
  },
  methods: {
    getUser: function(user) {
      this.user = user;
    }
  }
}
</script>
