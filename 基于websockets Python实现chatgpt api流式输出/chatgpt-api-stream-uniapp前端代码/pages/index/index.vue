<template>
	<view class="container">
		<view class="input_text">
			<textarea placeholder="请输入您的问题" v-model="message">
			</textarea>
		</view>
		<view class="bt">
			<button type="primary" @click="generateText">提问</button>
		</view>
		<view class="input_text" style="margin-top: 30rpx;">
			<view class="div2">
				{{ chatLog.join(" ") }}
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				socket: null,
				message: "",
				chatLog: [],
				startTime: null,
				endTime: null
			}
		},
		created() {
			uni.connectSocket({
				url: "ws://localhost:8765",
				success: function() {
					console.log("WebSocket连接成功！");
				},
			});
			uni.onSocketOpen(() => {
				console.log("WebSocket连接已打开");
			});
			uni.onSocketMessage((res) => {
				const data = JSON.parse(res.data);
				uni.sendSocketMessage({
					data: JSON.stringify({}),
				});
				let content = data.text
				if (content.content) {
					this.chatLog.push(content.content)
				}
			});
		},
		methods: {
			generateText() {
				console.log("开始发起请求：" + new Date()) // 记录开始时间
				this.chatLog = []
				uni.sendSocketMessage({
					data: JSON.stringify({
						dialogues: [{
							role: "user",
							content: this.message,
						}],
					}),
				});
			},
			closeSocket() {
				uni.closeSocket();
				console.log("WebSocket连接已关闭");
			},
		},
		beforeDestroy() {
			this.closeSocket();
		},
		computed: {
			formattedLog() {
				// 将 chatLog 数组格式化为可渲染的数组
				return this.chatLog.map(log => {
					return {
						role: log.role,
						content: typeof log.content === 'string' ? log.content : JSON.stringify(log.content),
					}
				})
			},
			timeDiff() {
				if (this.startTime && this.endTime) {
					// 计算时间差，以秒为单位
					return (this.endTime - this.startTime) / 1000;
				} else {
					return 0;
				}
			}
		},
		watch: {
			chatLog: function(newVal, oldVal) {
				if (newVal.length === 1) {
					this.startTime = new Date(); // 第一条消息，记录开始时间
				}
				if (newVal.length > 0 && newVal.length === oldVal.length) {
					this.endTime = new Date(); // 最后一条消息接收完毕，记录结束时间
					console.log(`时间差为 ${this.timeDiff} 秒`);
				}
			},
		}
	}
</script>

<style>
	.container {
		font-size: 14px;
		line-height: 24px;
		width: 100vw;
		height: 100vh;
	}

	.input_text {
		padding: 30rpx;
		width: 70vw;
		height: 30vh;
		margin: 0 auto;
		border: 1px solid #000000;
		border-radius: 10rpx;
	}

	.bt {
		margin: 0 auto;
		width: calc(70vw + 60rpx);
		margin-top: 30rpx;
	}
</style>