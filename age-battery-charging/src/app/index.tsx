import { Link } from 'expo-router';
import { useCallback, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { InfoRow } from '../components/InfoRow';
import { colors, spacing } from '../constants/theme';
import { useBatteryInfo } from '../hooks/useBatteryInfo';
import {
  batteryPercent,
  fillColor,
  stateColor,
  stateLabel,
  timeLabel,
} from '../utils/battery';

export default function HomeScreen() {
  const { info, loading, error, refresh } = useBatteryInfo();
  const [refreshing, setRefreshing] = useState(false);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await refresh();
    setRefreshing(false);
  }, [refresh]);

  const percent = info.level < 0 ? 0 : info.level;
  const status = stateLabel(info.state);

  return (
    <ScrollView
      style={styles.screen}
      contentContainerStyle={styles.content}>
      <Text style={styles.heading}>Battery Monitor</Text>
      <Text style={styles.subheading}>Live power state of your device</Text>

      <View style={styles.gaugeCard}>
        <Text style={styles.percent}>{batteryPercent(info.level)}</Text>
        <Text style={[styles.statusText, { color: stateColor(info.state) }]}>
          {status}
        </Text>

        <View style={styles.track}>
          <View
            style={[
              styles.fill,
              { width: `${percent * 100}%`, backgroundColor: fillColor(info.level) },
            ]}
          />
        </View>

        {loading ? (
          <ActivityIndicator color={colors.primary} style={styles.spinner} />
        ) : null}
      </View>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Current state</Text>
        <InfoRow label="Charging status" value={status} valueColor={stateColor(info.state)} />
        <InfoRow
          label="Low power mode"
          value={info.lowPowerMode ? 'On' : 'Off'}
          valueColor={info.lowPowerMode ? colors.warning : colors.text}
        />
        <InfoRow label="Last updated" value={timeLabel(info.updatedAt)} />
      </View>

      <Pressable style={styles.button} onPress={onRefresh} disabled={refreshing}>
        <Text style={styles.buttonText}>
          {refreshing ? 'Refreshing...' : 'Refresh now'}
        </Text>
      </Pressable>

      <Link href="/details" style={styles.link}>
        See details and recent readings
      </Link>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: spacing.lg,
    paddingBottom: spacing.xl,
  },
  heading: {
    color: colors.text,
    fontSize: 26,
    fontWeight: '800',
    marginTop: spacing.sm,
  },
  subheading: {
    color: colors.muted,
    fontSize: 14,
    marginBottom: spacing.lg,
  },
  gaugeCard: {
    backgroundColor: colors.surface,
    borderRadius: 20,
    padding: spacing.xl,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },
  percent: {
    color: colors.text,
    fontSize: 58,
    fontWeight: '800',
    letterSpacing: -2,
  },
  statusText: {
    fontSize: 16,
    fontWeight: '700',
    marginTop: spacing.xs,
    marginBottom: spacing.lg,
  },
  track: {
    width: '100%',
    height: 14,
    borderRadius: 7,
    backgroundColor: colors.surfaceAlt,
    overflow: 'hidden',
  },
  fill: {
    height: '100%',
    borderRadius: 7,
  },
  spinner: {
    marginTop: spacing.md,
  },
  error: {
    color: colors.danger,
    marginTop: spacing.md,
    textAlign: 'center',
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: spacing.md,
    marginTop: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
  },
  cardTitle: {
    color: colors.text,
    fontSize: 16,
    fontWeight: '700',
    marginBottom: spacing.sm,
  },
  button: {
    backgroundColor: colors.primary,
    borderRadius: 12,
    paddingVertical: spacing.md,
    alignItems: 'center',
    marginTop: spacing.lg,
  },
  buttonText: {
    color: colors.background,
    fontWeight: '800',
    fontSize: 15,
  },
  link: {
    color: colors.info,
    textAlign: 'center',
    marginTop: spacing.lg,
    fontSize: 14,
    fontWeight: '600',
  },
});
