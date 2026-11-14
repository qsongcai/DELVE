# DELVE 理论桥梁（保守版）：总体 KMeans 对齐作为显式兼容性条件

日期：2026-11-14（保守修订；撤回前一版"交换引理已证明总体最优"的声明）
状态：**条件性框架，非已证明的充分条件链**。

本版诚实记录：前一版试图用反拆分条件 $M_{\min}>S_{\max}^{\rm tot}$ 经一次局部交换推出"真环境是总体 KMeans 唯一最优"，该交换**不成立**。硬球模型只保证点的归属唯一，不阻止一个中心同时服务多个环境；对任意配置，移除中心的损失不能由条件最优 $V_e$ 控制，新增中心的收益也不等于 $M_{ef}$。因此本版把"总体 KMeans 一环境一中心"改为**直接假设的兼容性条件**，把 $\psi(q)>0$ 改为需要额外正则条件的条件性结论。

**正式命名（非循环定位）**：本桥梁的核心结果命名为 **Conditional Compatibility Theorem**——

$$\text{KMeans compatibility condition (A4')}\Longrightarrow\text{risk-gap recovery}.$$

它**不是**"recording feature separation $\Rightarrow$ partition recovery"的生成式结构桥梁，也不证明"EEG 协方差生成条件自动诱导 KMeans 最优"。全文以此名称引用，避免被读作已从生成机制非循环推出目标结论。

---

## 1. 理论对象与符号

令

$$X_r=A x_r^{(0)}+b\in\mathbb R^p,\qquad Z_r\in\{1,\dots,K\},$$

$$\mu_e=E[X\mid Z=e],\qquad\pi_e=P(Z=e),\qquad
\Delta=\min_{e\ne f}\|\mu_e-\mu_f\|.$$

总体 KMeans 风险：

$$R(c)=E\Big[\min_k\|X-c_k\|^2\Big],\qquad R^\star=\inf_c R(c).$$

### 1.1 与实际 recording 特征构造的对齐

实际特征 $X_r=A\big[\tfrac1{W_r}\sum_w\operatorname{vech}\{\log(\widehat\Sigma_{rw})\}\big]+b$，本模型是对**该实际特征**的条件模型：窗间依赖与非平稳进入残差；recording 方差由 $T_{\rm eff}$（诊断量）而非原始 $W_r$ 决定；LW/logm 的系统偏差是**中心偏差**、随机波动是噪声；$E[\mu_{e,T}]-\mu_e=O(1/T_w)$；环境内被试/session 异质允许、并入残差；$A,b$ 固定或训练冻结，全池 scaler 属 transductive 变体、不在固定变换定理内。

---

## 2. 生成模型与可独立成立的条件

位置模型 $X=\mu_Z+\xi_Z$，$E[\xi_e\mid Z=e]=0$。

**A1（权重）** $\pi_e\ge\pi_{\min}>0$。

**A2（集中，硬球）** $\|\xi_e\|\le\rho$ 几乎必然。

**A3（分离）** $\Delta>4\rho$。

### 引理 1（真中心最近邻分类器正确）——A1–A3 可独立支撑

对来自环境 $e$ 的 $X$，$\|X-\mu_e\|\le\rho$，而对 $f\ne e$，

$$\|X-\mu_f\|\ge\Delta-\rho>3\rho>\|X-\mu_e\|.$$

故 $g_\mu(X)=\arg\min_f\|X-\mu_f\|^2=Z$ 几乎必然。

**这条引理只证明"真中心能正确分类"，不证明真中心是总体 KMeans 最优。** 后者需要下面的显式兼容性条件。

---

## 3. 总体 KMeans 对齐：直接兼容性条件（A4'）

### 3.1 解释性量（诊断用，不构成证明）

$$V_e(m)=\inf_{c_1,\dots,c_m}E[\min_j\|X-c_j\|^2\mid Z=e],\quad
S_e(m)=V_e(1)-V_e(m),$$

$$M_{ef}=\frac{\pi_e\pi_f}{\pi_e+\pi_f}\|\mu_e-\mu_f\|^2.$$

$M_{\min}$、$S_{\max}^{\rm tot}=\max_e\pi_e\sup_m S_e(m)$ 提供"合并代价 vs 拆分收益"的直觉，但**不能**由 $M_{\min}>S_{\max}^{\rm tot}$ 直接推出总体最优，原因见开头与第 3.3 节。

正式口径（R1 节 2）：

> *The split/merge quantities are reported as descriptive diagnostics motivated by a possible anti-splitting mechanism. They do not verify A4' and are not used to establish population K-means optimality.*

即不写它们"支持 A4' 的机制"，避免间接复活已撤回的交换逻辑。

### 3.2 条件 A4'（直接假设）

**Population K-means alignment condition**：在固定 $K$、固定变换下，总体 KMeans 风险的每个全局最优解都恰好把一个中心分配给每个环境，即

$$\mathcal C^\star=\{c:R(c)=R^\star\}
=\{(\mu_1,\dots,\mu_K)\text{ 的标签置换}\}.$$

这是对**总体目标函数几何形状**的直接条件，而不是从 split/merge 量推出的结论。

可与之等价或近邻表述的是 k-means 文献中的**成本分离（cost/ε-separation）**条件：$(K-1)$-中心最优成本相对 $K$-中心最优成本有严格、稳定的间隙，从而把 $K$ 个中心绑定到 $K$ 个自然分组（Ostrovsky–Rabani–Schulman–Wan 一系的 ε-separation 框架）。**引用前须回到原文核对精确陈述与常数，本蓝图不预设具体常数。**

### 3.3 为什么不能用局部交换替代 A4'

- 硬球分离只保证**点**不跨球，中心仍可落在球间、其 Voronoi 单元同时服务多个环境，无法按"服务哪个环境"干净分组。
- 移除中心的损失 $\pi_e[V_e(m-1)-V_e(m)]$ 仅当当前 $m$ 中心已实现条件最优、剩余中心实现 $V_e(m-1)$ 时才成立，任意配置无此保证。
- $M_{ef}$ 是两完整环境用各自均值再合并的 between 项，不等于当前多中心配置中给 $f$ 增中心实际消除的风险。

故"一次移动风险下降"未建立，"重复移动"无依据。强路线（在严格结构化的分布与配置类上补全捕获引理）留作未来工作，本版不声称已完成。

---

## 4. 定理 A（条件性）：对齐条件下的总体识别

**定理 A**：若 A1–A3 与 **A4'** 同时成立，则对某个置换 $\pi$，

$$P\{g_{c^\star}(X)\ne\pi(Z)\}=0.$$

**证明**：A4' 直接给出最优中心为 $\mu_e$ 的置换；引理 1 给出该配置零误差。$\square$

注意这里的识别力来自**被显式假设的 A4'**，不是由更底层生成条件推出。

---

## 5. 定理 B（条件性）：正风险间隙需要额外正则条件

$$\mathcal C_q=\{c:\mathrm{Err}(c,Z)\ge q\},\qquad
\psi(q)=\inf_{c\in\mathcal C_q}\{R(c)-R^\star\}.$$

仅"最优分类器无正概率 tie"**不足以**保证 $\mathcal C_q$ 闭或 $\mathrm{Err}$ 连续。

**A6（显式正则条件）**：错分率函数 $\mathrm{Err}(c,Z)$ 在中心域上（上半）连续，等价地所有水平集 $\mathcal C_q$ 闭。对绝对连续、密度在 Voronoi 边界附近有界的分布，该条件成立（边界管状体质量随宽度趋于零），但须作为显式条件陈述。

**定理 B**：在定理 A 条件外加 A6，对满足 $\mathcal C_q\ne\varnothing$ 的 $q>0$，$\psi(q)>0$。

**证明**：定理 A 下 $\mathcal C^\star$ 误差为零，$\mathcal C_q\cap\mathcal C^\star=\varnothing$；A6 使 $\mathcal C_q$ 闭，紧域上 $R-R^\star$ 的下确界被取到且为正。$\square$

### 5.1 定量下界（局部，A5 为独立强假设）

**A5（二次增长，独立强假设）** $R(c)-R^\star\ge\kappa\,d(c,\mathcal C^\star)^2$。

**边界 margin**：$P(X\in\mathcal M_t)\le C_{\rm margin}t^\beta$（普通 $\beta=1$）。

**三个限制（R1 节 6）**：① 中心扰动须处于 Voronoi 边界的**局部稳定区域**，label 翻转只由边界管状体引起；② margin 条件须对**变换后 $X$** 的分布成立，不是对原始协方差或窗口特征；③ A5 独立于 margin，**不能由 margin 自动推出**。

在局部稳定区域内，$\mathrm{Err}(c)\le C_{\rm margin}d(c,\mathcal C^\star)^\beta$。因此限定

$$\boxed{0<q\le q_0,\qquad
\psi(q)\ge\kappa\Big(\frac{q}{C_{\rm margin}}\Big)^{2/\beta}}$$

$\beta=1$ 时 $\psi(q)\ge(\kappa/C_{\rm margin}^2)q^2$。**$q_0$ 的来源须写清**：它是局部线性化仍成立的最大错分水平，由边界稳定区半径（最近中心到边界的最小距离）经 margin 关系反解确定，超出该范围局部 Lipschitz 不再保证。本版不声称全局定量下界；$\kappa$、$C_{\rm margin}$ 非自我认证。

---

## 6. 定理 C（有限样本转移，标准界保留）

统一经验偏差 $\varepsilon_M$ 与近似优化误差 $\delta_{\rm opt}$ 给出标准界

$$R_T(\widehat c)-R^\star\le 2\varepsilon_M+\delta_{\rm opt}.$$

**定理 C**：在 A4'、A6 成立（从而 $\psi(q)>0$ 有定义）的前提下，若 $2\varepsilon_M+\delta_{\rm opt}<\psi(q)$，则 $\mathrm{Err}(\widehat c,Z)<q$。

该 excess-risk 界本身不依赖被撤回的交换，可独立成立；但整条恢复结论仍以 A4'、A6 为条件。

---

## 7. Sub-Gaussian 版本（仅处理集中半径）

若 $P(\|X-\mu_e\|>t\mid e)\le C\exp(-ct^2/\sigma_e^2)$，取 $\rho_T=\sigma\sqrt{\tfrac1c\log\tfrac{CK}{\delta}}$，以至少 $1-\delta$ 概率所有特征落在 $\rho_T$ 球内。这只替代硬 $\rho$、给出集中事件的尾概率；**不修复交换缺口**，A4' 仍须显式假设。

---

## 8. EEG 外部案例（external case，非理论验证）

平衡 30/30/30、20 seeds、scaled 空间（anti_splitting_diagnostic.py）：

| 诊断量 | mean | range |
|---|---|---|
| $\min M_{ef}$ | 1.199 | [1.053, 1.397] |
| $\max\pi_e S_e(2)$ | .772 | [.609, .989] |
| 分离噪声比 $\Delta/\max\sigma$ | .907 | [.793, 1.021] |

EEG 不满足 A3（.91 vs 要求 4），A4' 又无独立诊断，故真实数据只能支持：

> *recording-level covariance features contain source-associated structure under a balanced known-$K$ diagnostic analysis.*

不能支持"所提条件解释了观察到的恢复"。理论是**边界模型（boundary model）**、不是 EEG 结果的解释模型；EEG 是该条件之外的外部案例，展示 known-K 可恢复与 blind-K 失败。诊断不构成定理 A–C 的实证。

---

## 9. 诚实边界与最终口径

- 本版**不包含**"从生成条件推出总体 KMeans 唯一最优"的已证明结果；A4' 是显式兼容性假设，A6 是显式正则假设，A5 是独立强假设。
- 可声称：在固定 $K$、固定/冻结变换、A1–A3 且总体对齐条件 A4' 与正则条件 A6 成立时，潜在环境划分与总体 KMeans 一致、$\psi(q)>0$，并经标准集中界转移到全局经验 KMeans。
- 不可声称：反拆分 split/merge 量已证明总体最优；自动 K、全池 scaler、有限初始化 Lloyd 被覆盖；真实无标签 EEG 验证了这些条件。
- 强路线（结构化分布类上的捕获/交换严格证明）列为未来工作。
