<template>
  <div>
    <p>Event comment List</p>
    <p>イベント数：{{eventcomments.count}}</p>
    <p>nextページ：{{ eventcomments.next }}</p>
    <p>previousページ：{{ eventcomments.previous }}</p>
    <div v-for="(eventcomment, key) in eventcomments.results" :key="key">
      <hr>
        <p>コメントID：{{ eventcomment.id }}</p>
        <p>コメントユーザーID：{{ eventcomment.user }}</p>
        <p>コメントユーザー名：{{ eventcomment.first_name }}</p>
        <p>コメントユーザーアイコン：{{ eventcomment.icon }}</p>
        <p>コメント：{{ eventcomment.comment }}</p>
        <p>コメント日：{{ eventcomment.brief_updated_at }}</p>
      <hr>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BaseEventComment',
  data() {
    return {
      eventcomments: [],
    };
  },
  mounted :function() {
    this.axios
      .get('api/events/' + this.$route.query.id + '/comments/')
      .then(response => {this.eventcomments = response.data})
      .catch(error => console.log(error))
  },
}
</script>


<style scoped>
</style>
