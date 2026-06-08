const krwFormatter = new Intl.NumberFormat("ko-KR", {
  maximumFractionDigits: 0,
});

const decimalPriceFormatter = new Intl.NumberFormat("ko-KR", {
  minimumFractionDigits: 0,
  maximumFractionDigits: 4,
});

const marketVolumeFormatter = new Intl.NumberFormat("ko-KR", {
  minimumFractionDigits: 0,
  maximumFractionDigits: 3,
});

export function formatKrwPrice(value: number): string {
  if (Math.abs(value) >= 1_000) {
    return krwFormatter.format(value);
  }

  return decimalPriceFormatter.format(value);
}

export function formatChangeRate(value: number): string {
  if (value === 0) {
    return "0.00%";
  }

  const sign = value > 0 ? "+" : "";
  return `${sign}${(value * 100).toFixed(2)}%`;
}

export function formatCompactKoreanAmount(value: number): string {
  const eok = Math.round(value / 100_000_000);
  return `${krwFormatter.format(eok)}억원`;
}

export function formatMarketSize(value: number): string {
  return value.toFixed(4);
}

export function formatMarketVolume(value: number): string {
  return marketVolumeFormatter.format(value);
}
