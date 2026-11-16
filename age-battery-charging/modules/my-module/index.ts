import { requireNativeModule } from 'expo';
import type { BatteryDetailsModule } from './src/BatteryDetailsModule';

export type { BatteryDetails } from './src/BatteryDetailsModule';

export default requireNativeModule<BatteryDetailsModule>('BatteryDetails');
