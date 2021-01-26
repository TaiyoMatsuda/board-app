<template>
  <div>
    <p>Event List</p>
    <div v-for="(event, key) in events" :key="key">
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
export default {
  name: 'EventList',
  data() {
    return {
      events: []
    };
  },
  mounted :function(){
    this.axios
      .get('https://jsonplaceholder.typicode.com/users/')
      .then(response => {this.events = response.data})
      .catch(error => console.log(error))
  }
}
</script>


<style scoped>
</style>
