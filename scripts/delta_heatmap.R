library(ggplot2)
library(dplyr)
library(patchwork)

#### READ DATA ####
df <- read.csv("../results/data/tidy_results.csv")
benchmarks_ordered <- read.csv("../results/data/blimp_benchmarks_ordered.csv")

#### PREPROCESSING ####

# Rename column
df <- df %>%
  rename(blimp_delta = blimp_delta_all_seed_avg)

# Y-axis ordering
df$blimp_benchmark <- factor(df$blimp_benchmark, levels=benchmarks_ordered$benchmark, ordered=T)

# Group by and calculate means (delta)
blimp_delta_means <- df %>%
  select(corpus, arch, seed, blimp_benchmark, blimp_delta, filter_target) %>%
  group_by(corpus, arch, blimp_benchmark, filter_target) %>%
  summarise(blimp_delta = mean(blimp_delta)) %>%
  mutate(blimp_delta = round(blimp_delta, 3))

# Group by and calculate means (averages)
blimp_acc_means <- df %>%
  select(corpus, arch, seed, blimp_benchmark, blimp_acc, filter_target) %>%
  group_by(corpus, arch, blimp_benchmark, filter_target) %>%
  summarise(blimp_acc = mean(blimp_acc)) %>%
  mutate(blimp_acc = round(blimp_acc, 3))

blimp_delta_means$filter_target <- as.logical(blimp_delta_means$filter_target)

#### PLOTTING ####

# Make each of the four groups of columns

plt_lstm_full_acc <- ggplot(data = blimp_acc_means[blimp_acc_means$corpus == "full" & blimp_acc_means$arch == "lstm", ], aes(x = corpus, y = blimp_benchmark, fill = blimp_acc)) +
  geom_tile() +
  geom_text(aes(label = blimp_acc), size = 3) +
  scale_fill_gradient2(high = "#3a983a", midpoint = 0.5) +
  labs(x = "", y = "") +
  ggtitle("acc.") +
  scale_y_discrete(limits=rev) +
  theme(legend.position = "none",
        axis.text.x = element_text(angle = 45, hjust = 1),
        axis.text.y = element_text(angle = 45, vjust = 1, hjust = 1),
        plot.margin = unit(c(0, 0, 0, 0), "cm"),
        plot.title = element_text(hjust = 0.5))


plt_lstm_nofull <- ggplot(data = blimp_delta_means[blimp_delta_means$corpus != "full" & blimp_delta_means$arch == "lstm", ], aes(x = corpus, y = blimp_benchmark, fill = blimp_delta)) +
  geom_tile() +
  geom_tile(data = blimp_delta_means[blimp_delta_means$filter_target, ], fill = NA, color = "black", linewidth = 1) +
  geom_text(aes(label = blimp_delta), size = 3) +
  scale_fill_gradient2(high = "#3a983a", midpoint = 0) +
  labs(x = "", y = "") +
  ggtitle(expression(Delta)) +
  scale_y_discrete(limits=rev) +
  theme(legend.position = "none",
        axis.text.x = element_text(angle = 45, hjust = 1),
        axis.text.y = element_text(angle = 45, vjust = 1, hjust = 1),
        # axis.text.y = element_blank(),
        #axis.ticks.y = element_blank(),
        plot.margin = unit(c(0, 0, 0, 0), "cm"),
        plot.title = element_text(hjust = 0.5))

plt_transformer_full_acc <- ggplot(data = blimp_acc_means[blimp_acc_means$corpus == "full" & blimp_acc_means$arch == "transformer", ], aes(x = corpus, y = blimp_benchmark, fill = blimp_acc)) +
  geom_tile() +
  geom_text(aes(label = blimp_acc), size = 3) +
  scale_fill_gradient2(high = "#3a983a", midpoint = 0.5) +
  labs(x = "", y = "") +
  ggtitle("acc.") +
  scale_y_discrete(limits=rev) +
  theme(legend.position = "none",
        axis.text.x = element_text(angle = 45, hjust = 1),
        axis.text.y = element_text(angle = 45, vjust = 1, hjust = 1),
        plot.margin = unit(c(0, 0, 0, 0), "cm"),
        plot.title = element_text(hjust = 0.5))

plt_transformer_nofull <- ggplot(data = blimp_delta_means[blimp_delta_means$corpus != "full" & blimp_delta_means$arch == "transformer", ], aes(x = corpus, y = blimp_benchmark, fill = blimp_delta)) +
  geom_tile() +
  geom_tile(data = blimp_delta_means[blimp_delta_means$filter_target, ], fill = NA, color = "black", linewidth = 1) +
  geom_text(aes(label = blimp_delta), size = 3) +
  scale_fill_gradient2(high = "#3a983a", midpoint = 0) +
  labs(x = "", y = "") +
  ggtitle(expression(Delta)) +
  scale_y_discrete(limits=rev) +
  theme(legend.position = "none",
        axis.text.x = element_text(angle = 45, hjust = 1),
        axis.text.y = element_text(angle = 45, vjust = 1, hjust = 1),
        plot.margin = unit(c(0, 0, 0, 0), "cm"),
        plot.title = element_text(hjust = 0.5))



# Compose plots

titles <- wrap_elements(panel = grid::textGrob("LSTM")) + wrap_elements(panel = grid::textGrob("Transformer"))
plts <- (plt_lstm_full_acc | plot_spacer() | plt_lstm_nofull | plot_spacer() | plt_transformer_full_acc | plot_spacer() | plt_transformer_nofull) +
  plot_layout(axes="collect", widths = c(2, 0.1, 15, 0.5, 2, 0.1, 15))
plt <- titles / plts  + # janky way of adding the supertitles, but couldn't make it work a better way
  plot_layout(heights = c(0.012, 1))

#### SAVE ####
ggsave("../results/graphs/blimp_delta_full_acc_heatmap.pdf", plt, width = 18, height = 16, create.dir = TRUE)
