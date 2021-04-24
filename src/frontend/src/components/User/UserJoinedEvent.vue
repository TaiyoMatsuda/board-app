<template>
  <div>
    <p>Join Event List</p>
    <p>イベント数：{{events.count}}</p>
    <p>nextページ：{{ events.next }}</p>
    <p>previousページ：{{ events.previous }}</p>    
    <div v-for="(event, key) in events.results" :key="key">
      <hr>
        <p>イベントID:{{ event.id }}</p>
        <p>イベントタイトル：{{ event.title }}</p>
        <p>イベントイメージ:{{ event.image }}</p>
        <p>時間:{{ event.event_time }}</p>
        <p>開催地:{{ event.address }}</p>
        <p>参加者数:{{ event.participant_count }}</p>
        <router-link :to="{ name: 'Event', query: { id: event.id}}">
          more
        </router-link>
      <hr>
    </div>
  </div>
</template>

<script>
import { axios } from '@/main.js'

export default {
  name: 'JoinedEvent',
  data() {
    return {
      events: []
    };
  },
  mounted :function(){
    axios.get('api/users/' + this.$route.query.id + '/joinedEvents/')
      .then(response => {this.events = response.data})
      .catch(error => console.log(error))
  }
}
</script>


<style scoped>
</style>
