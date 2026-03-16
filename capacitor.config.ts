import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.coligame.app',
  appName: 'Coligame',
  webDir: 'src',
  server: {
    androidScheme: 'https'
  }
};

export default config;
