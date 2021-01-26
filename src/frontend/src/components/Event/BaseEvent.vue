<template>
  <div>
    <p>{{this.$route.query.id}}</p>
    <p>イベントID：{{ events.id }}</p>
    <p>タイトル：{{ events.title }}</p>
    <p>イベント紹介：{{ events.description }}</p>
    <p>主催者ID：{{ events.organizer }}</p>
    <p>主催者名：{{ events.organizer_first_name }}</p>
    <p>主催者アイコン：{{ events.organizer_icon }}</p>
    <p>イベントイメージ：{{ events.image }}</p>
    <p>イベント時間：{{ events.event_time }}</p>
    <p>イベント場所：{{ events.address }}</p>
    <p>料金：{{ events.fee }}</p>
    <p>ステータス：{{ events.status }}</p>
    <p>更新時間：{{ events.brief_updated_at }}</p>
  </div>
</template>

<script>
export default {
  name: 'BaseEvent',
  data() {
    return {
      events: []
    };
  },
  mounted :function(){
    console.log('https://jsonplaceholder.typicode.com/users/' + this.$route.query.id)
    this.axios
      .get('https://jsonplaceholder.typicode.com/users/' + this.$route.query.id)
      .then(response => {this.events = response.data})
      .catch(error => console.log(error))
  }
}
</script>


<style scoped>
</style>
