<?php
session_start();
require_once __DIR__ . '/includes/database_connect.php';

$total_sessions = 0;
if (isset($pdo)) {
    try {
        $total_sessions = (int) $pdo->query("SELECT COUNT(*) FROM Bookings WHERE status IN ('Confirmed','Completed')")->fetchColumn();
    } catch (PDOException $e) {
        $total_sessions = 0;
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta content="width=device-width, initial-scale=1.0" name="viewport">
    <title>ShuttleSync | Precision Badminton Management</title>
    <?php include __DIR__ . '/includes/tailwind_config.php'; ?>
    <style>
        html { scroll-behavior: smooth; }

        .reveal {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        .reveal.visible {
            opacity: 1;
            transform: translateY(0);
        }

        .stat-number {
            font-variant-numeric: tabular-nums;
        }
    </style>
</head>
<body class="bg-white text-on-background antialiased">

<?php include __DIR__ . '/includes/nav_bar.php'; ?>

<main>

    <!-- ==========================================
         HERO
    ========================================== -->
    <section class="relative pt-32 pb-20 px-5 md:px-12 min-h-[70vh] flex items-center overflow-hidden">
        <div class="absolute inset-0 bg-cover bg-center" style="background-image: url('https://lh3.googleusercontent.com/gps-cs-s/AHRPTWnLDlXBylc3vYQOxMS5ATkSvP6fstDWnISENNKSLLGTG8zkVMGnY5GmK5PHPHIvdPcBXVO0hxR-US_NyY09rMySORoAUvzqWzf_YqS4u2faYerr_q13rEDTmMGal5vr9akapelR=s680-w680-h510-rw');"></div>
        <div class="absolute inset-0 bg-gradient-to-r from-black/80 via-black/60 to-black/30"></div>
        <div class="relative z-10 max-w-6xl mx-auto w-full">
            <div class="max-w-2xl">
                <p class="text-accent-light text-xs font-bold tracking-[0.25em] uppercase mb-4">ShuttleSync</p>
                <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight tracking-tight mb-6">
                    Book courts, play better.
                </h1>
                <p class="text-lg text-white/80 leading-relaxed mb-10 max-w-lg">
                    Real-time court reservations, AI-powered performance analysis, and everything you need to elevate your badminton game.
                </p>
                <div class="flex flex-col sm:flex-row gap-3">
                    <a href="/courtbooking" class="inline-flex items-center justify-center bg-accent text-white px-8 py-3.5 rounded-lg font-bold text-sm hover:bg-accent-dark transition-all active:scale-95">
                        Book a Court
                    </a>
                    <a href="/aimovementanalysis" class="inline-flex items-center justify-center bg-white/10 backdrop-blur-sm border border-white/30 text-white px-8 py-3.5 rounded-lg font-bold text-sm hover:bg-white/20 transition-all active:scale-95">
                        Try AI Coach
                    </a>
                </div>
            </div>
        </div>
    </section>


    <!-- ==========================================
         STATS
    ========================================== -->
    <section class="py-16 px-5 md:px-12 bg-surface border-y border-outline-variant/40">
        <div class="max-w-6xl mx-auto">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
                <div class="reveal">
                    <div class="text-3xl md:text-4xl font-bold text-on-background stat-number mb-1">8</div>
                    <div class="text-xs text-on-surface-variant font-semibold uppercase tracking-[0.15em]">Courts</div>
                </div>
                <div class="reveal">
                    <div class="text-3xl md:text-4xl font-bold text-on-background stat-number mb-1">500<span class="text-accent">+</span></div>
                    <div class="text-xs text-on-surface-variant font-semibold uppercase tracking-[0.15em]">Players</div>
                </div>
                <div class="reveal">
                    <div class="text-3xl md:text-4xl font-bold text-on-background stat-number mb-1" id="sessionCounter" data-target="<?php echo $total_sessions; ?>">0</div>
                    <div class="text-xs text-on-surface-variant font-semibold uppercase tracking-[0.15em]">Sessions Booked</div>
                </div>
                <div class="reveal">
                    <div class="text-3xl md:text-4xl font-bold text-on-background stat-number mb-1">100<span class="text-accent">+</span></div>
                    <div class="text-xs text-on-surface-variant font-semibold uppercase tracking-[0.15em]">Daily Players</div>
                </div>
            </div>
        </div>
    </section>


    <!-- ==========================================
         FEATURES
    ========================================== -->
    <section class="py-24 px-5 md:px-12">
        <div class="max-w-6xl mx-auto">
            <div class="mb-14 reveal">
                <p class="text-accent text-xs font-bold tracking-[0.25em] uppercase mb-3">Features</p>
                <h2 class="text-3xl md:text-4xl font-bold text-on-background tracking-tight">Everything you need to win.</h2>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <a href="/courtbooking" class="group block p-8 rounded-2xl border border-outline-variant/40 hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300 reveal">
                    <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center mb-5">
                        <span class="material-symbols-outlined text-primary text-[22px]">calendar_month</span>
                    </div>
                    <h3 class="text-lg font-bold text-on-background mb-2">Court Booking</h3>
                    <p class="text-sm text-on-surface-variant leading-relaxed">Reserve courts in real time. Instant confirmation, zero double-bookings.</p>
                    <span class="inline-flex items-center gap-1 text-primary text-sm font-bold mt-5 group-hover:translate-x-1 transition-transform">
                        Book now <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
                    </span>
                </a>

                <a href="/aimovementanalysis" class="group block p-8 rounded-2xl border border-outline-variant/40 hover:border-accent/40 hover:shadow-lg hover:shadow-accent/5 transition-all duration-300 reveal">
                    <div class="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-5">
                        <span class="material-symbols-outlined text-accent text-[22px]">psychology</span>
                    </div>
                    <h3 class="text-lg font-bold text-on-background mb-2">AI Coach</h3>
                    <p class="text-sm text-on-surface-variant leading-relaxed">Biomechanical analysis powered by MediaPipe. Track form and improve every stroke.</p>
                    <span class="inline-flex items-center gap-1 text-accent text-sm font-bold mt-5 group-hover:translate-x-1 transition-transform">
                        Try free <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
                    </span>
                </a>

                <a href="/ecommerce" class="group block p-8 rounded-2xl border border-outline-variant/40 hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300 reveal">
                    <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center mb-5">
                        <span class="material-symbols-outlined text-primary text-[22px]">storefront</span>
                    </div>
                    <h3 class="text-lg font-bold text-on-background mb-2">Pro Shop</h3>
                    <p class="text-sm text-on-surface-variant leading-relaxed">Shop gear and pay securely with PayPal, GCash, or cash at the counter.</p>
                    <span class="inline-flex items-center gap-1 text-primary text-sm font-bold mt-5 group-hover:translate-x-1 transition-transform">
                        Shop now <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
                    </span>
                </a>
            </div>
        </div>
    </section>


    <!-- ==========================================
         WHY SHUTTLESYNC
    ========================================== -->
    <section class="py-24 px-5 md:px-12 bg-surface">
        <div class="max-w-6xl mx-auto">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
                <div class="reveal">
                    <p class="text-accent text-xs font-bold tracking-[0.25em] uppercase mb-3">Why ShuttleSync</p>
                    <h2 class="text-3xl md:text-4xl font-bold text-on-background tracking-tight mb-10">Built for players who take it seriously.</h2>

                    <div class="space-y-7">
                        <div class="flex gap-4">
                            <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0 mt-0.5">
                                <span class="material-symbols-outlined text-primary text-[18px]">hub</span>
                            </div>
                            <div>
                                <h4 class="text-sm font-bold text-on-background mb-1">Centralized Management</h4>
                                <p class="text-sm text-on-surface-variant leading-relaxed">Court schedules, player analytics, and payments in one place.</p>
                            </div>
                        </div>
                        <div class="flex gap-4">
                            <div class="w-8 h-8 rounded-full bg-accent/10 flex items-center justify-center shrink-0 mt-0.5">
                                <span class="material-symbols-outlined text-accent text-[18px]">model_training</span>
                            </div>
                            <div>
                                <h4 class="text-sm font-bold text-on-background mb-1">AI-Powered Coaching</h4>
                                <p class="text-sm text-on-surface-variant leading-relaxed">Real biomechanical analysis using pose detection technology.</p>
                            </div>
                        </div>
                        <div class="flex gap-4">
                            <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0 mt-0.5">
                                <span class="material-symbols-outlined text-primary text-[18px]">update</span>
                            </div>
                            <div>
                                <h4 class="text-sm font-bold text-on-background mb-1">Live Reservations</h4>
                                <p class="text-sm text-on-surface-variant leading-relaxed">Real-time updates across all devices. Zero confusion.</p>
                            </div>
                        </div>
                        <div class="flex gap-4">
                            <div class="w-8 h-8 rounded-full bg-accent/10 flex items-center justify-center shrink-0 mt-0.5">
                                <span class="material-symbols-outlined text-accent text-[18px]">lock</span>
                            </div>
                            <div>
                                <h4 class="text-sm font-bold text-on-background mb-1">Secure Payments</h4>
                                <p class="text-sm text-on-surface-variant leading-relaxed">PayPal, GCash, and cash. Every transaction protected.</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="reveal">
                    <div class="bg-surface-container-low rounded-2xl border border-outline-variant/40 p-8">
                        <div class="flex items-center gap-3 mb-6">
                            <div class="w-2 h-2 rounded-full bg-green-500"></div>
                            <span class="text-xs font-bold text-on-surface-variant uppercase tracking-[0.15em]">Live Availability</span>
                        </div>
                        <div class="space-y-3">
                            <?php
                            if (isset($pdo)) {
                                try {
                                    $courts = $pdo->query("SELECT name, status FROM Courts ORDER BY court_id ASC LIMIT 8")->fetchAll();
                                    foreach ($courts as $court):
                                        $statusColor = match($court['status']) {
                                            'Available' => 'bg-green-500',
                                            'Booked' => 'bg-accent',
                                            'Maintenance' => 'bg-yellow-500',
                                            default => 'bg-gray-400'
                                        };
                            ?>
                            <div class="flex items-center justify-between py-3 px-4 rounded-lg bg-white border border-outline-variant/30">
                                <span class="text-sm font-bold text-on-background"><?php echo htmlspecialchars($court['name']); ?></span>
                                <div class="flex items-center gap-2">
                                    <span class="w-2 h-2 rounded-full <?php echo $statusColor; ?>"></span>
                                    <span class="text-xs font-semibold text-on-surface-variant"><?php echo htmlspecialchars($court['status']); ?></span>
                                </div>
                            </div>
                            <?php
                                    endforeach;
                                } catch (PDOException $e) {
                                    for ($i = 1; $i <= 8; $i++):
                            ?>
                            <div class="flex items-center justify-between py-3 px-4 rounded-lg bg-white border border-outline-variant/30">
                                <span class="text-sm font-bold text-on-background">Court <?php echo $i; ?></span>
                                <div class="flex items-center gap-2">
                                    <span class="w-2 h-2 rounded-full bg-green-500"></span>
                                    <span class="text-xs font-semibold text-on-surface-variant">Available</span>
                                </div>
                            </div>
                            <?php
                                    endfor;
                                }
                            }
                            ?>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>


    <!-- ==========================================
         CTA
    ========================================== -->
    <section class="py-24 px-5 md:px-12">
        <div class="max-w-6xl mx-auto text-center reveal">
            <h2 class="text-3xl md:text-4xl font-bold text-on-background tracking-tight mb-4">Ready to play?</h2>
            <p class="text-on-surface-variant mb-10 max-w-md mx-auto">Join hundreds of players already using ShuttleSync to book courts, analyze form, and level up.</p>
            <div class="flex flex-col sm:flex-row gap-3 justify-center">
                <a href="/authentication/register" class="inline-flex items-center justify-center bg-primary text-white px-8 py-3.5 rounded-lg font-bold text-sm hover:bg-primary-dark transition-all active:scale-95">
                    Get Started Free
                </a>
                <a href="/courtbooking" class="inline-flex items-center justify-center border border-outline-variant text-on-background px-8 py-3.5 rounded-lg font-bold text-sm hover:bg-surface transition-all active:scale-95">
                    Browse Courts
                </a>
            </div>
        </div>
    </section>

</main>

<?php include __DIR__ . '/includes/footer.php'; ?>
<?php include __DIR__ . '/includes/mobile_nav.php'; ?>

<script>
// Scroll reveal
const reveals = document.querySelectorAll('.reveal');
const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
reveals.forEach(el => io.observe(el));

// Session counter animation
const counter = document.getElementById('sessionCounter');
if (counter) {
    const target = parseInt(counter.dataset.target) || 0;
    const cObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.dataset.counted) {
                entry.dataset.counted = 'true';
                const duration = 1800;
                const start = performance.now();
                function update(now) {
                    const progress = Math.min((now - start) / duration, 1);
                    const eased = 1 - Math.pow(1 - progress, 3);
                    counter.textContent = Math.floor(eased * target).toLocaleString();
                    if (progress < 1) requestAnimationFrame(update);
                }
                requestAnimationFrame(update);
            }
        });
    }, { threshold: 0.5 });
    cObserver.observe(counter);
}
</script>

</body>
</html>
