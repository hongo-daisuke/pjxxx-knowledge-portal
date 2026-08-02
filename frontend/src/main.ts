import 'element-plus/dist/index.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import jaLocale from 'element-plus/es/locale/lang/ja'

import App from './App.vue'
import { configureAmplify } from './plugins/awsconfig'
import router from './router'

configureAmplify()

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: jaLocale })
app.mount('#app')
