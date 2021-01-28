<template>
  <div class="create_update_event">
    <h1>This is a create and update event page</h1>
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
    <BaseEvent v-on:parentGetEvent="getEvent"></BaseEvent>
  </div>
</template>

<script>
import BaseEvent from '@/components/Event/BaseEvent.vue'

export default {
  name: 'Event',
  data() {
    return {
      events: []
    }
  },
  components: {
    BaseEvent,
  },
  methods: {
    getEvent: function(events) {
      this.events = events;
    }
  }
}
</script>
