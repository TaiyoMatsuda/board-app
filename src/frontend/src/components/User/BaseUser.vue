<template>
  <div>
    <p>ユーザID:{{ user.id }}</p>
    <p>ユーザ名:{{ user.first_name }}</p>
    <p>ユーザ姓:{{ user.family_name }}</p>
    <p>紹介文:{{ user.introduction }}</p>
    <p>ガイドフラグ:{{ user.is_guide }}</p>
    <p>ユーザアイコン:{{ user.icon_url }}</p>
  </div>
</template>
<script>
export default {
  name: 'BaseUser',
  data() {
    return {
      user: []
    }
  },
  mounted :function(){
    this.axios
      .get('api/users/' + this.$route.query.id + '/')
      .then(response => {this.user = response.data})
      .catch(error => console.log(error))
  }
}
</script>
