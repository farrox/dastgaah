#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

static int cmp_double(const void *a, const void *b) {
    double da = *(const double *)a;
    double db = *(const double *)b;
    return (da > db) - (da < db);
}

static double median_arr(const double *arr, int n) {
    if (n <= 0) return NAN;
    double *tmp = (double *)malloc(n * sizeof(double));
    int m = 0;
    for (int i = 0; i < n; i++) {
        if (isfinite(arr[i])) tmp[m++] = arr[i];
    }
    if (m == 0) { free(tmp); return NAN; }
    qsort(tmp, m, sizeof(double), cmp_double);
    double res = (m % 2 == 1) ? tmp[m / 2] : 0.5 * (tmp[m / 2 - 1] + tmp[m / 2]);
    free(tmp);
    return res;
}

static double mad_cents_arr(const double *freqs, int n, double f_ref) {
    if (n < 3 || !isfinite(f_ref) || f_ref <= 0.0) return 999.0;
    double *c = (double *)malloc(n * sizeof(double));
    int m = 0;
    for (int i = 0; i < n; i++) {
        if (isfinite(freqs[i]) && freqs[i] > 0.0) {
            c[m++] = 1200.0 * log2(freqs[i] / f_ref);
        }
    }
    if (m < 3) { free(c); return 999.0; }
    double med = median_arr(c, m);
    for (int i = 0; i < m; i++) c[i] = fabs(c[i] - med);
    double mad = 1.4826 * median_arr(c, m);
    free(c);
    return mad;
}

static inline double cents_diff(double a, double b) {
    if (!isfinite(a) || !isfinite(b) || a <= 0.0 || b <= 0.0) return NAN;
    return 1200.0 * log2(a / b);
}

// In-place radix-2 Cooley-Tukey complex FFT (dir = +1 for forward, -1 for inverse)
void cfft(double *re, double *im, int n, int dir) {
    int i, j;
    for (i = 1, j = 0; i < n; i++) {
        int bit = n >> 1;
        for (; j & bit; bit >>= 1) j ^= bit;
        j ^= bit;
        if (i < j) {
            double tr = re[i]; re[i] = re[j]; re[j] = tr;
            double ti = im[i]; im[i] = im[j]; im[j] = ti;
        }
    }
    for (int len = 2; len <= n; len <<= 1) {
        double ang = -2.0 * M_PI / len * dir;
        double wlen_r = cos(ang), wlen_i = sin(ang);
        for (i = 0; i < n; i += len) {
            double wr = 1.0, wi = 0.0;
            int half = len >> 1;
            for (j = 0; j < half; j++) {
                int u = i + j, v = i + j + half;
                double vr = re[v] * wr - im[v] * wi;
                double vi = re[v] * wi + im[v] * wr;
                re[v] = re[u] - vr;
                im[v] = im[u] - vi;
                re[u] += vr;
                im[u] += vi;
                double nwr = wr * wlen_r - wi * wlen_i;
                wi = wr * wlen_i + wi * wlen_r;
                wr = nwr;
            }
        }
    }
    if (dir == -1) {
        for (i = 0; i < n; i++) {
            re[i] /= n;
            im[i] /= n;
        }
    }
}

// Parabolic-interpolated YIN (CMND) estimator
double yin_f0_cmnd(const double *x, int n, double sr, double fmin, double fmax, double thresh, double *out_ap) {
    int tau_min = (int)(sr / fmax);
    int tau_max = (int)(sr / fmin) + 2;
    int W = n - tau_max - 1;
    if (W < tau_max || tau_max <= tau_min + 2) {
        if (out_ap) *out_ap = 1.0;
        return NAN;
    }
    int nfft = 1;
    while (nfft < n + W) nfft <<= 1;
    double *re1 = (double *)calloc(nfft, sizeof(double));
    double *im1 = (double *)calloc(nfft, sizeof(double));
    double *re2 = (double *)calloc(nfft, sizeof(double));
    double *im2 = (double *)calloc(nfft, sizeof(double));
    for (int i = 0; i < W; i++) re1[i] = x[i];
    for (int i = 0; i < n; i++) re2[i] = x[i];
    cfft(re1, im1, nfft, 1);
    cfft(re2, im2, nfft, 1);
    for (int i = 0; i < nfft; i++) {
        double r = re1[i] * re2[i] + im1[i] * im2[i];
        double im = re1[i] * im2[i] - im1[i] * re2[i];
        re1[i] = r;
        im1[i] = im;
    }
    cfft(re1, im1, nfft, -1);

    double *cum_sq = (double *)malloc((n + 1) * sizeof(double));
    cum_sq[0] = 0.0;
    for (int i = 0; i < n; i++) cum_sq[i + 1] = cum_sq[i] + x[i] * x[i];
    double E0 = cum_sq[W];

    double *d = (double *)malloc((tau_max + 1) * sizeof(double));
    double *dp = (double *)malloc((tau_max + 1) * sizeof(double));
    d[0] = 0.0;
    dp[0] = 1.0;
    double running_sum = 0.0;
    for (int tau = 1; tau <= tau_max; tau++) {
        double Etau = cum_sq[tau + W] - cum_sq[tau];
        double val = E0 + Etau - 2.0 * re1[tau];
        if (val < 0.0) val = 0.0;
        d[tau] = val;
        running_sum += val;
        dp[tau] = (running_sum > 1e-18) ? (val * tau / running_sum) : 1.0;
    }

    int best_tau = -1;
    for (int tau = tau_min; tau < tau_max; tau++) {
        if (dp[tau] < thresh && dp[tau] <= dp[tau - 1] && dp[tau] <= dp[tau + 1]) {
            best_tau = tau;
            break;
        }
    }
    if (best_tau < 0) {
        best_tau = tau_min;
        double min_val = dp[tau_min];
        for (int tau = tau_min + 1; tau < tau_max; tau++) {
            if (dp[tau] < min_val) {
                min_val = dp[tau];
                best_tau = tau;
            }
        }
    }

    double ap = dp[best_tau];
    double tau_refined = (double)best_tau;
    if (best_tau >= 1 && best_tau < tau_max) {
        double a = d[best_tau - 1], b = d[best_tau], c = d[best_tau + 1];
        double denom = a - 2.0 * b + c;
        if (fabs(denom) > 1e-15) {
            double delta = 0.5 * (a - c) / denom;
            if (delta > -1.0 && delta < 1.0) tau_refined += delta;
        }
    }

    free(re1); free(im1); free(re2); free(im2);
    free(cum_sq); free(d); free(dp);
    if (out_ap) *out_ap = ap;
    return sr / tau_refined;
}

// Multi-Harmonic Least-Squares + Phase-Vocoder Instantaneous Frequency Estimator
// with Pre-Onset Spectral Drone/Decay Subtraction and Odd/Even Subharmonic Verification
double harmonic_ls_f0(
    const double *x, int n, const double *x_pre, int n_pre,
    double sr, double fmin, double fmax,
    double f_yin_hint, double drone_freq,
    double *out_hnr_db, double *out_harm_std_cents, int *out_n_active_harms
) {
    if (n < 512) return NAN;
    int hop_pv = 64;
    int n_win = n - hop_pv;
    if (n_win < 256) { hop_pv = 0; n_win = n; }
    int npad = 1;
    while (npad < n_win * 4) npad <<= 1;
    if (npad < 16384) npad = 16384;

    double *re1 = (double *)calloc(npad, sizeof(double));
    double *im1 = (double *)calloc(npad, sizeof(double));
    double *re2 = (double *)calloc(npad, sizeof(double));
    double *im2 = (double *)calloc(npad, sizeof(double));

    double sum_w1 = 0.0;
    for (int i = 0; i < n_win; i++) {
        double w = 0.5 * (1.0 - cos(2.0 * M_PI * i / (n_win - 1)));
        sum_w1 += w;
        re1[i] = x[i] * w;
        if (hop_pv > 0) re2[i] = x[i + hop_pv] * w;
    }
    cfft(re1, im1, npad, 1);
    if (hop_pv > 0) cfft(re2, im2, npad, 1);

    int half = npad >> 1;
    double df = sr / (double)npad;
    double *mag = (double *)malloc((half + 1) * sizeof(double));
    double *mag_enh = (double *)malloc((half + 1) * sizeof(double));
    double *logmag = (double *)malloc((half + 1) * sizeof(double));
    for (int k = 0; k <= half; k++) {
        double m = hypot(re1[k], im1[k]) / (sum_w1 + 1e-12);
        mag[k] = m;
        mag_enh[k] = m;
        logmag[k] = log(m + 1e-15);
    }

    if (x_pre != NULL && n_pre >= 512) {
        double *pre_re = (double *)calloc(npad, sizeof(double));
        double *pre_im = (double *)calloc(npad, sizeof(double));
        int nw_pre = n_pre < npad ? n_pre : npad;
        double sum_wp = 0.0;
        for (int i = 0; i < nw_pre; i++) {
            double w = 0.5 * (1.0 - cos(2.0 * M_PI * i / (nw_pre - 1)));
            sum_wp += w;
            pre_re[i] = x_pre[i] * w;
        }
        cfft(pre_re, pre_im, npad, 1);
        for (int k = 0; k <= half; k++) {
            double mp = hypot(pre_re[k], pre_im[k]) / (sum_wp + 1e-12);
            double m = mag[k];
            double gain = (m + 1e-12) / (m + 0.85 * mp + 1e-12);
            mag_enh[k] = m * gain;
        }
        free(pre_re); free(pre_im);
    }

    int K_comb = 6;
    double best_score = -1e30;
    double f_seed = (isfinite(f_yin_hint) && f_yin_hint >= fmin && f_yin_hint <= fmax) ? f_yin_hint : sqrt(fmin * fmax);

    for (double f = fmin; f <= fmax; f *= 1.000866) {
        double score = 0.0;
        for (int h = 1; h <= K_comb; h++) {
            double fh = f * h;
            if (fh >= sr * 0.45) break;
            int idx = (int)round(fh / df);
            if (idx < 2 || idx >= half - 2) continue;
            double m_loc = mag_enh[idx];
            for (int d = -2; d <= 2; d++) {
                if (mag_enh[idx + d] > m_loc) m_loc = mag_enh[idx + d];
            }
            double f_half = f * (h - 0.5);
            int idx_half = (int)round(f_half / df);
            double m_half = (idx_half >= 2 && idx_half < half - 2) ? mag_enh[idx_half] : 0.0;

            double w_h = pow((double)h, -0.35);
            score += w_h * (m_loc * m_loc - 0.65 * m_half * m_half);
        }
        if (isfinite(f_yin_hint) && f_yin_hint > 0.0) {
            double dc = fabs(1200.0 * log2(f / f_yin_hint));
            if (dc < 35.0) score *= (1.0 + 0.35 * cos(dc / 35.0 * M_PI * 0.5));
        }
        if (score > best_score) {
            best_score = score;
            f_seed = f;
        }
    }

    if (isfinite(f_yin_hint) && f_yin_hint >= fmin && f_yin_hint <= fmax) {
        double ratio = f_seed / f_yin_hint;
        if (fabs(ratio - 2.0) < 0.08 || fabs(ratio - 3.0) < 0.08) {
            f_seed = f_yin_hint;
        }
    }

    // Anti-subharmonic guard: if f_seed has negligible odd-harmonic energy (h=1, 3) compared to even harmonics (h=2, 4),
    // promote f_seed *= 2.0
    if (2.0 * f_seed <= fmax) {
        double e_odd = 0.0, e_even = 0.0;
        for (int h = 1; h <= 4; h++) {
            int b_lo = (int)floor(f_seed * h * 0.975 / df);
            int b_hi = (int)ceil(f_seed * h * 1.025 / df);
            if (b_lo < 2) b_lo = 2;
            if (b_hi >= half - 2) b_hi = half - 2;
            double pk_m = 0.0;
            for (int b = b_lo; b <= b_hi; b++) if (mag[b] > pk_m) pk_m = mag[b];
            if (h % 2 == 1) e_odd += pk_m * pk_m;
            else e_even += pk_m * pk_m;
        }
        if (e_even > 0.0 && e_odd < 0.12 * e_even) {
            f_seed *= 2.0;
        }
    }

    int k_lo = (int)(fmin / df);
    double f_upper = (sr * 0.4 < 6.0 * fmax) ? (sr * 0.4) : (6.0 * fmax);
    int k_hi = (int)(f_upper / df);
    double total_energy = 0.0;
    for (int k = k_lo; k <= k_hi && k < half; k++) total_energy += mag[k] * mag[k];
    double mean_bin_power = total_energy / (double)(k_hi - k_lo + 1 + 1e-9);

    double sum_wk_kf = 0.0;
    double sum_wk_k2 = 0.0;
    double harm_energy = 0.0;
    double f0_ests[8];
    double f0_weights[8];
    int n_active = 0;

    for (int h = 1; h <= 6; h++) {
        double fh_expect = f_seed * h;
        if (fh_expect >= sr * 0.42) break;
        int b_lo = (int)floor(fh_expect * 0.978 / df);
        int b_hi = (int)ceil(fh_expect * 1.022 / df);
        if (b_lo < 2) b_lo = 2;
        if (b_hi >= half - 2) b_hi = half - 2;
        if (b_hi <= b_lo) continue;

        int pk = b_lo;
        double pk_mag = mag[b_lo];
        for (int b = b_lo + 1; b <= b_hi; b++) {
            if (mag[b] > pk_mag) {
                pk_mag = mag[b];
                pk = b;
            }
        }
        if (pk_mag * pk_mag < 3.0 * mean_bin_power) continue;

        if (drone_freq > 0.0) {
            double dc_seed_drone = fabs(1200.0 * log2(f_seed / drone_freq));
            double dc_pk_drone = fabs(1200.0 * log2((pk * df) / drone_freq));
            double dc_pk_drone2 = fabs(1200.0 * log2((pk * df) / (2.0 * drone_freq)));
            if (dc_seed_drone > 45.0 && (dc_pk_drone < 15.0 || dc_pk_drone2 < 15.0)) {
                continue;
            }
        }

        double a = logmag[pk - 1], b = logmag[pk], c = logmag[pk + 1];
        double denom = a - 2.0 * b + c;
        double delta_par = (fabs(denom) > 1e-12) ? (0.5 * (a - c) / denom) : 0.0;
        if (delta_par < -1.0) delta_par = -1.0;
        if (delta_par > 1.0) delta_par = 1.0;
        double fh_par = (pk + delta_par) * df;

        double fh_use = fh_par;
        if (hop_pv > 0) {
            double phi1 = atan2(im1[pk], re1[pk]);
            double phi2 = atan2(im2[pk], re2[pk]);
            double dphi_exp = 2.0 * M_PI * pk * hop_pv / (double)npad;
            double dphi_err = (phi2 - phi1) - dphi_exp;
            dphi_err = fmod(dphi_err + M_PI, 2.0 * M_PI);
            if (dphi_err < 0.0) dphi_err += 2.0 * M_PI;
            dphi_err -= M_PI;
            double fh_pv = (pk + dphi_err * npad / (2.0 * M_PI * hop_pv)) * df;
            if (fabs(fh_pv - fh_par) < 0.75 * df) {
                fh_use = 0.5 * (fh_par + fh_pv);
            }
        }

        double stiffness_damp = 1.0 / (1.0 + 0.12 * (h - 1) * (h - 1));
        double w_h = (mag_enh[pk] * mag_enh[pk]) * stiffness_damp;

        sum_wk_kf += w_h * h * fh_use;
        sum_wk_k2 += w_h * h * h;
        f0_ests[n_active] = fh_use / (double)h;
        f0_weights[n_active] = w_h * h * h;
        n_active++;

        for (int b = pk - 2; b <= pk + 2; b++) {
            if (b >= 0 && b <= half) harm_energy += mag[b] * mag[b];
        }
    }

    double f0_final = (sum_wk_k2 > 0.0 && n_active > 0) ? (sum_wk_kf / sum_wk_k2) : f_seed;

    double std_cents = 0.0;
    if (n_active >= 2) {
        double wsum = 0.0, var_c = 0.0;
        for (int i = 0; i < n_active; i++) {
            double dc = 1200.0 * log2(f0_ests[i] / f0_final);
            var_c += f0_weights[i] * dc * dc;
            wsum += f0_weights[i];
        }
        std_cents = sqrt(var_c / (wsum + 1e-15));
    }

    double noise_energy = total_energy - harm_energy;
    if (noise_energy < 1e-12) noise_energy = 1e-12;
    double hnr_db = 10.0 * log10((harm_energy + 1e-12) / noise_energy);

    if (out_hnr_db) *out_hnr_db = hnr_db;
    if (out_harm_std_cents) *out_harm_std_cents = std_cents;
    if (out_n_active_harms) *out_n_active_harms = n_active;

    free(re1); free(im1); free(re2); free(im2);
    free(mag); free(mag_enh); free(logmag);
    return f0_final;
}

// Narrowband Harmonic-Locked Hilbert Transform (NB-Hilbert on highest-SIR harmonic k*)
int nb_hilbert_track(
    const double *x, int n, double sr, double f_target, double rel_bw,
    double *env, double *inst_f
) {
    int nfft = 1;
    while (nfft < n * 2) nfft <<= 1;
    double *re = (double *)calloc(nfft, sizeof(double));
    double *im = (double *)calloc(nfft, sizeof(double));
    double mean = 0.0;
    for (int i = 0; i < n; i++) mean += x[i];
    mean /= (n > 0 ? n : 1);
    for (int i = 0; i < n; i++) re[i] = x[i] - mean;
    cfft(re, im, nfft, 1);

    double df = sr / (double)nfft;
    int half = nfft >> 1;

    int h_best = 1;
    double best_score = -1.0;
    for (int h = 1; h <= 4; h++) {
        double fh = f_target * h;
        if (fh >= sr * 0.4) break;
        int k_in_lo = (int)floor(fh * 0.982 / df);
        int k_in_hi = (int)ceil(fh * 1.018 / df);
        int k_out_lo = (int)floor(fh * 0.89 / df);
        int k_out_hi = (int)ceil(fh * 1.11 / df);
        if (k_out_lo < 1) k_out_lo = 1;
        if (k_out_hi >= half) k_out_hi = half - 1;
        double e_sig = 0.0, e_clutter = 1e-12;
        for (int k = k_out_lo; k <= k_out_hi; k++) {
            double p = re[k] * re[k] + im[k] * im[k];
            if (k >= k_in_lo && k <= k_in_hi) e_sig += p;
            else e_clutter += p;
        }
        double sir = e_sig / (e_clutter + 1e-12);
        double score = e_sig * sqrt(sir) / pow((double)h, 0.35);
        if (score > best_score) {
            best_score = score;
            h_best = h;
        }
    }

    double f_center = f_target * h_best;
    double f_lo = f_center * (1.0 - rel_bw);
    double f_hi = f_center * (1.0 + rel_bw);
    double taper = (f_hi - f_lo) * 0.25;

    for (int k = 0; k < nfft; k++) {
        if (k == 0 || k >= half) {
            re[k] = 0.0;
            im[k] = 0.0;
            continue;
        }
        double fk = k * df;
        double w = 0.0;
        if (fk >= f_lo && fk <= f_hi) {
            if (fk < f_lo + taper) {
                w = 0.5 * (1.0 - cos(M_PI * (fk - f_lo) / taper));
            } else if (fk > f_hi - taper) {
                w = 0.5 * (1.0 - cos(M_PI * (f_hi - fk) / taper));
            } else {
                w = 1.0;
            }
        }
        re[k] *= 2.0 * w;
        im[k] *= 2.0 * w;
    }

    cfft(re, im, nfft, -1);

    double *raw_if = (double *)malloc(n * sizeof(double));
    for (int i = 0; i < n; i++) {
        env[i] = hypot(re[i], im[i]);
    }
    raw_if[0] = f_target;
    for (int i = 1; i < n; i++) {
        double cross_r = re[i - 1] * re[i] + im[i - 1] * im[i];
        double cross_i = re[i - 1] * im[i] - im[i - 1] * re[i];
        double dphi = atan2(cross_i, cross_r);
        double fi = (dphi * sr / (2.0 * M_PI)) / (double)h_best;
        if (fi < f_target * 0.5 || fi > f_target * 1.5) fi = f_target;
        raw_if[i] = fi;
    }
    raw_if[0] = raw_if[1];

    int k_half = (int)(0.003 * sr);
    if (k_half < 2) k_half = 2;
    for (int i = 0; i < n; i++) {
        int a = i - k_half; if (a < 0) a = 0;
        int b = i + k_half; if (b >= n) b = n - 1;
        double sw = 0.0, sf = 0.0;
        for (int j = a; j <= b; j++) {
            double w = env[j] * env[j] + 1e-12;
            sw += w;
            sf += w * raw_if[j];
        }
        inst_f[i] = sf / sw;
    }

    free(re); free(im); free(raw_if);
    return h_best;
}

void compute_spectral_flux(const double *x, int n, double sr, int frame_len, int hop, double *flux_out, int n_frames) {
    double *re = (double *)calloc(frame_len, sizeof(double));
    double *im = (double *)calloc(frame_len, sizeof(double));
    int half = frame_len >> 1;
    double *prev_mag = (double *)calloc(half + 1, sizeof(double));
    double *win = (double *)malloc(frame_len * sizeof(double));
    for (int i = 0; i < frame_len; i++) win[i] = 0.5 * (1.0 - cos(2.0 * M_PI * i / (frame_len - 1)));

    double df = sr / (double)frame_len;
    int k_lo = (int)(80.0 / df);
    int k_hi = (int)(4500.0 / df);
    if (k_hi > half) k_hi = half;

    for (int f = 0; f < n_frames; f++) {
        int start = f * hop;
        for (int i = 0; i < frame_len; i++) {
            re[i] = (start + i < n) ? (x[start + i] * win[i]) : 0.0;
            im[i] = 0.0;
        }
        cfft(re, im, frame_len, 1);
        double flux = 0.0;
        for (int k = k_lo; k <= k_hi; k++) {
            double m = log1p(100.0 * hypot(re[k], im[k]));
            double diff = m - prev_mag[k];
            if (diff > 0.0) flux += diff;
            prev_mag[k] = m;
        }
        flux_out[f] = (f == 0) ? 0.0 : flux;
    }
    free(re); free(im); free(prev_mag); free(win);
}

// Full-track 4-stage strike extractor in C
// Returns number of extracted trusted strikes written into output arrays (up to max_out)
int extract_track_strikes_c(
    const double *x, int n_samples, double sr,
    double fmin, double fmax, double drone_freq,
    double max_wobble_plat_c, double min_conf,
    int max_out,
    double *t_out, double *f_out, double *conf_out,
    double *wob_plat_out, double *wob_sus_out,
    double *drift_out, double *bend_out, int *method_out
) {
    int frame_len = 2048;
    int hop = 1024;
    int n_frames = (n_samples - frame_len) / hop;
    if (n_frames < 10) return 0;

    double *flux = (double *)malloc(n_frames * sizeof(double));
    compute_spectral_flux(x, n_samples, sr, frame_len, hop, flux, n_frames);

    // 88th percentile threshold
    double *flux_sorted = (double *)malloc(n_frames * sizeof(double));
    memcpy(flux_sorted, flux, n_frames * sizeof(double));
    qsort(flux_sorted, n_frames, sizeof(double), cmp_double);
    int idx88 = (int)round(0.88 * (n_frames - 1));
    double thresh = flux_sorted[idx88];
    free(flux_sorted);

    int min_dist = (int)(0.18 * sr / hop);
    if (min_dist < 1) min_dist = 1;
    int *peaks = (int *)malloc(n_frames * sizeof(int));
    int n_peaks = 0;
    for (int i = 1; i < n_frames - 1; i++) {
        if (flux[i] >= thresh && flux[i] >= flux[i - 1] && flux[i] >= flux[i + 1]) {
            if (n_peaks == 0 || (i - peaks[n_peaks - 1]) >= min_dist) {
                peaks[n_peaks++] = i;
            } else if (flux[i] > flux[peaks[n_peaks - 1]]) {
                peaks[n_peaks - 1] = i;
            }
        }
    }
    free(flux);

    int win_n = (int)(0.50 * sr);
    int i05 = (int)(0.05 * sr);
    int i35 = (int)(0.35 * sr);
    int n_mid = i35 - i05;
    int pre_len = (int)(0.10 * sr);
    int plat_len = (int)(0.14 * sr);
    int step_len = (int)(0.015 * sr);

    double *env = (double *)malloc(win_n * sizeof(double));
    double *inst_f = (double *)malloc(win_n * sizeof(double));
    double *sub_if = (double *)malloc((plat_len / 4 + 4) * sizeof(double));

    int count = 0;
    for (int p = 0; p < n_peaks && count < max_out; p++) {
        double ot = peaks[p] * (double)hop / sr;
        int off = (int)(ot * sr);
        if (off + win_n >= n_samples) continue;

        const double *p_mid = x + off + i05;
        int pre_off = off - (int)(0.11 * sr);
        const double *p_pre = (pre_off >= 0) ? (x + pre_off) : NULL;
        int n_pre = (pre_off >= 0) ? pre_len : 0;

        // Stage 1: Initial YIN + Multi-Harmonic LS/PV on [0.05s, 0.35s]
        double ap_fixed = 1.0;
        double f_yin_fixed = yin_f0_cmnd(p_mid, n_mid, sr, fmin, fmax, 0.15, &ap_fixed);
        double hnr_fixed = 0.0, hstd_fixed = 0.0;
        int nharms_fixed = 0;
        double f_hmls_fixed = harmonic_ls_f0(
            p_mid, n_mid, p_pre, n_pre, sr, fmin, fmax, f_yin_fixed, drone_freq,
            &hnr_fixed, &hstd_fixed, &nharms_fixed
        );
        if (isfinite(f_yin_fixed) && isfinite(f_hmls_fixed) && fabs(cents_diff(2.0 * f_yin_fixed, f_hmls_fixed)) < 30.0) {
            f_yin_fixed *= 2.0;
        }
        double f_seed = isfinite(f_hmls_fixed) ? f_hmls_fixed : f_yin_fixed;
        if (!isfinite(f_seed) || f_seed < fmin || f_seed > fmax) continue;

        // Stage 2: Harmonic-Locked Narrowband Hilbert Trajectory & Attack/Sustain Diagnostics
        nb_hilbert_track(x + off, win_n, sr, f_seed, 0.065, env, inst_f);

        int i_att0 = (int)(0.015 * sr), i_att1 = (int)(0.055 * sr);
        int i_sus0 = (int)(0.080 * sr), i_sus1 = (int)(0.360 * sr);
        double f_att = median_arr(inst_f + i_att0, i_att1 - i_att0);
        double f_sus = median_arr(inst_f + i_sus0, i_sus1 - i_sus0);
        double attack_bend_c = cents_diff(f_att, f_sus);
        double wobble_sus_c = mad_cents_arr(inst_f + i_sus0, i_sus1 - i_sus0, f_sus);

        int i_sus_mid = (i_sus0 + i_sus1) / 2;
        double f_early = median_arr(inst_f + i_sus0, i_sus_mid - i_sus0);
        double f_late = median_arr(inst_f + i_sus_mid, i_sus1 - i_sus_mid);
        double dt_sus = (i_sus1 - i_sus0) / (2.0 * sr);
        double drift_c_per_s = cents_diff(f_late, f_early) / (dt_sus > 0.05 ? dt_sus : 0.05);

        // Stage 3: Adaptive 140 ms Stationary Plateau Selection
        double max_env = 1e-12;
        for (int i = 0; i < win_n; i++) if (env[i] > max_env) max_env = env[i];

        double best_plat_score = 1e9;
        int best_plat_start = (int)(0.08 * sr);
        int st_end = win_n - plat_len - (int)(0.02 * sr);
        for (int st = (int)(0.060 * sr); st <= st_end; st += step_len) {
            double sum_e = 0.0;
            int ne = 0;
            for (int i = st; i < st + plat_len; i += 8) { sum_e += env[i]; ne++; }
            double mean_e = sum_e / (ne > 0 ? ne : 1);
            if (mean_e < 0.18 * max_env) continue;

            int ns = 0;
            for (int i = st; i < st + plat_len; i += 4) sub_if[ns++] = inst_f[i];
            double f_med = median_arr(sub_if, ns);
            double wob = mad_cents_arr(sub_if, ns, f_med);
            double f_h1 = median_arr(sub_if, ns / 2);
            double f_h2 = median_arr(sub_if + ns / 2, ns - ns / 2);
            double drift_loc = fabs(cents_diff(f_h2, f_h1));
            double score = wob + 0.6 * drift_loc - 3.5 * (mean_e / max_env);
            if (score < best_plat_score) {
                best_plat_score = score;
                best_plat_start = st;
            }
        }

        // Stage 4: Parabolic YIN + Multi-Harmonic LS/PV on the Stationary Plateau & Arbitration/Gating
        const double *p_plat = x + off + best_plat_start;
        double ap_plat = 1.0;
        double f_yin_plat = yin_f0_cmnd(p_plat, plat_len, sr, fmin, fmax, 0.15, &ap_plat);
        double hnr_plat = 0.0, hstd_plat = 0.0;
        int nharms_plat = 0;
        double f_hmls_plat = harmonic_ls_f0(
            p_plat, plat_len, p_pre, n_pre, sr, fmin, fmax, f_yin_plat, drone_freq,
            &hnr_plat, &hstd_plat, &nharms_plat
        );
        if (isfinite(f_yin_plat) && isfinite(f_hmls_plat) && fabs(cents_diff(2.0 * f_yin_plat, f_hmls_plat)) < 30.0) {
            f_yin_plat *= 2.0;
        }
        double f_hilb_plat = median_arr(inst_f + best_plat_start, plat_len);
        double wobble_plat_c = mad_cents_arr(inst_f + best_plat_start, plat_len, f_hilb_plat);

        double d_hy = fabs(cents_diff(f_hmls_plat, f_yin_plat));
        double d_hh = fabs(cents_diff(f_hmls_plat, f_hilb_plat));
        double d_yh = fabs(cents_diff(f_yin_plat, f_hilb_plat));

        double f_upgraded = NAN;
        int method_id = 0;
        if (isfinite(d_hy) && d_hy <= 28.0 && isfinite(d_hh) && d_hh <= 28.0) {
            double w_hm = (nharms_plat >= 2) ? 0.55 : 0.40;
            double w_hi = 0.25;
            double w_yi = 1.0 - w_hm - w_hi;
            f_upgraded = pow(f_hmls_plat, w_hm) * pow(f_hilb_plat, w_hi) * pow(f_yin_plat, w_yi);
            method_id = 1; // HMLS+NBH+YIN
        } else if (isfinite(d_hy) && d_hy <= 28.0) {
            double w_hm = (nharms_plat >= 2) ? 0.65 : 0.45;
            f_upgraded = pow(f_hmls_plat, w_hm) * pow(f_yin_plat, 1.0 - w_hm);
            method_id = 2; // HMLS+YIN
        } else if (isfinite(d_hh) && d_hh <= 25.0 && nharms_plat >= 2) {
            f_upgraded = 0.65 * f_hmls_plat + 0.35 * f_hilb_plat;
            method_id = 3; // HMLS+NBH
        } else if (isfinite(d_yh) && d_yh <= 25.0 && ap_plat < 0.20) {
            f_upgraded = 0.60 * f_yin_plat + 0.40 * f_hilb_plat;
            method_id = 4; // YIN+NBH
        } else {
            continue; // Reject unresolved / split / ghost strikes
        }

        if (!isfinite(f_upgraded) || f_upgraded < fmin || f_upgraded > fmax) continue;

        double min_d = d_hy;
        if (isfinite(d_hh) && d_hh < min_d) min_d = d_hh;
        if (isfinite(d_yh) && d_yh < min_d) min_d = d_yh;

        double s_per = 1.0 - ap_plat / 0.38;
        if (s_per < 0.0) s_per = 0.0; if (s_per > 1.0) s_per = 1.0;
        double s_stab = exp(-wobble_plat_c / 18.0);
        double s_agree = exp(-min_d / 18.0);
        double s_hnr = (hnr_plat + 5.0) / 25.0;
        if (s_hnr < 0.0) s_hnr = 0.0; if (s_hnr > 1.0) s_hnr = 1.0;
        double conf = 100.0 * (0.30 * s_per + 0.30 * s_stab + 0.25 * s_agree + 0.15 * s_hnr);

        // Apply stationarity & confidence gate
        if (wobble_plat_c > max_wobble_plat_c || conf < min_conf) continue;

        t_out[count] = ot;
        f_out[count] = f_upgraded;
        conf_out[count] = conf;
        wob_plat_out[count] = wobble_plat_c;
        wob_sus_out[count] = wobble_sus_c;
        drift_out[count] = isfinite(drift_c_per_s) ? drift_c_per_s : 0.0;
        bend_out[count] = isfinite(attack_bend_c) ? attack_bend_c : 0.0;
        method_out[count] = method_id;
        count++;
    }

    free(peaks);
    free(env);
    free(inst_f);
    free(sub_if);
    return count;
}

