<template>
  <div>
    <router-link :to="{ name: 'UpdateUser', query: { id: user.id}}">
      edit
    </router-link>
    <p>ユーザID:{{ user.id }}</p>
    <p>ユーザ名:{{ user.short_name }}</p>
    <p>紹介文:{{ user.introduction }}</p>
    <p>ガイドフラグ:{{ user.is_guide }}</p>
    <p>ユーザアイコン:{{ user.icon_url }}</p>
  </div>
</template>
<script>
export default {
  name: 'ReadUser',
  data() {
    return {
      user: []
    }
  },
  mounted :function(){
    this.axios
      .get('api/users/' + this.$route.query.id + '/read/')
      .then(response => {this.user = response.data})
      .catch(error => console.log(error))
  }
}
</script>
