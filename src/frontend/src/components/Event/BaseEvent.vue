<template>
  <div>
    <p>イベントID：{{ event.id }}</p>
    <p>タイトル：{{ event.title }}</p>
    <p>イベント紹介：{{ event.description }}</p>
    <p>主催者ID：{{ event.organizer }}</p>
    <p>主催者名：{{ event.organizer_full_name }}</p>
    <p>主催者アイコン：{{ event.organizer_icon }}</p>
    <p>イベントイメージ：{{ event.image }}</p>
    <p>イベント時間：{{ event.event_time }}</p>
    <p>イベント場所：{{ event.address }}</p>
    <p>料金：{{ event.fee }}</p>
    <p>ステータス：{{ event.status }}</p>
    <p>更新時間：{{ event.brief_updated_at }}</p>
  </div>
</template>
<script>
export default {
  name: 'BaseEvent',
  data() {
    return {
      event: []
    }
  },
  mounted :function(){
    this.axios
      .get('api/events/' + this.$route.query.id + '/')
      .then(response => {this.event = response.data})
      .catch(error => console.log(error))
  }
}
</script>