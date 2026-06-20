# Target-domain calibration sample-size audit

This audit tests how many target-domain calibration records are needed to repair cross-region conformal coverage.
The source model is fixed. Only a scalar target offset and conformal residual width are estimated from the sampled target calibration rows.

## Median coverage and width

| Window | Calibration rows | Median coverage | IQR coverage | Median width |
|---:|---:|---:|---:|---:|
| 2s | 10 | 0.867 | 0.811-0.924 | 1.980 |
| 2s | 25 | 0.862 | 0.805-0.910 | 1.786 |
| 2s | 50 | 0.888 | 0.863-0.911 | 2.039 |
| 2s | 100 | 0.905 | 0.869-0.923 | 2.161 |
| 2s | 250 | 0.906 | 0.879-0.934 | 2.214 |
| 2s | 1000 | 0.902 | 0.889-0.922 | 2.172 |
| 5s | 10 | 0.882 | 0.800-0.921 | 1.926 |
| 5s | 25 | 0.841 | 0.805-0.899 | 1.759 |
| 5s | 50 | 0.882 | 0.859-0.920 | 2.008 |
| 5s | 100 | 0.902 | 0.873-0.925 | 2.080 |
| 5s | 250 | 0.903 | 0.876-0.930 | 2.105 |
| 5s | 1000 | 0.901 | 0.889-0.917 | 2.128 |

## Source-domain conformal baseline

| Window | Median source coverage | Median source width |
|---:|---:|---:|
| 2s | 0.468 | 1.228 |
| 5s | 0.298 | 0.826 |

Smallest tested calibration size with median and IQR coverage inside 0.85-0.95: 50 records.

Interpretation: very small target samples can move median coverage toward nominal, 50 records meet the tested IQR stability criterion, and 100 records place both tested windows close to 0.90 median coverage. Interval width remains a region-specific quantity. This supports the paper's boundary claim without adding a new model.
