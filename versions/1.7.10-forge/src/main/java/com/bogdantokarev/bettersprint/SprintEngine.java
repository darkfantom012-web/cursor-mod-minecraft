package com.bogdantokarev.bettersprint;

/**
 * Better Sprint - core acceleration logic.
 * Pure Java, no Minecraft classes, shared by every loader/version port.
 *
 * Author: Bogdan_Tokarev
 */
public final class SprintEngine {

    /** Vanilla sprint speed: 5.612 m/s == 0.2806 blocks per tick. */
    public static final double BASE_SPRINT = 0.2806D;
    /** Natural cap: 8.612 m/s == 0.4306 blocks per tick. */
    public static final double MAX_SPEED = 0.4306D;
    /** Maximum boost factor (~ +53.5%). */
    public static final double MAX_BOOST = MAX_SPEED / BASE_SPRINT - 1.0D;

    /** +10% of base speed per second of sprinting. */
    public static final double GAIN_PER_TICK = 0.10D / 20.0D;
    /** Normal boost bleed-off after stopping. */
    public static final double DECAY_PER_TICK = 0.30D / 20.0D;
    /** Faster bleed-off after hitting a mob while running on the ground. */
    public static final double HIT_DECAY_PER_TICK = 0.75D / 20.0D;

    /** Boost needed for inertia slide / camera sway to kick in. */
    public static final double EFFECT_THRESHOLD = 0.20D;
    /** Camera yaw change (degrees per tick) treated as a "sharp" turn. */
    public static final double TURN_THRESHOLD = 5.0D;
    /** Maximum camera roll in degrees. */
    public static final double MAX_ROLL = 5.5D;

    /** Current boost, 0 .. MAX_BOOST. */
    public double boost;
    /** Smoothed camera roll in degrees (negative = tilt left). */
    public double roll;
    /** Sideways push for this tick (blocks/tick, + = to the right of the look direction). */
    public double sway;
    /** Inertia slide factor 0..1, non-zero only right after a sharp stop. */
    public double slide;
    /** Horizontal speed (blocks/tick) kept by the inertia slide. */
    public double slideSpeed;
    /** Last horizontal move direction, used while sliding. */
    public double slideDirX, slideDirZ;

    private int hitDecayTicks;
    private double targetRoll;
    private double prevYaw;
    private boolean hasPrevYaw;
    private boolean wasSprinting;

    /** Called when the player attacks an entity. Air hits keep the speed, ground hits bleed it off. */
    public void onAttack(boolean airborne) {
        if (!airborne) {
            hitDecayTicks = 30;
        }
    }

    public double yawDelta(double yaw) {
        if (!hasPrevYaw) {
            prevYaw = yaw;
            hasPrevYaw = true;
            return 0.0D;
        }
        double d = yaw - prevYaw;
        while (d > 180.0D) d -= 360.0D;
        while (d < -180.0D) d += 360.0D;
        prevYaw = yaw;
        return d;
    }

    public void reset() {
        boost = 0;
        roll = 0;
        targetRoll = 0;
        sway = 0;
        slide = 0;
        slideSpeed = 0;
        hitDecayTicks = 0;
        wasSprinting = false;
    }

    /**
     * @param sprinting   player is sprinting right now
     * @param movingInput player actually holds a movement key
     * @param yawDelta    camera yaw change this tick, degrees
     * @param speed       current horizontal speed, blocks/tick
     * @param dirX,dirZ   normalized horizontal move direction (0,0 if standing)
     */
    public void tick(boolean sprinting, boolean movingInput, double yawDelta,
                     double speed, double dirX, double dirZ) {

        if (hitDecayTicks > 0) hitDecayTicks--;

        boolean accelerating = sprinting && movingInput && hitDecayTicks == 0;

        if (accelerating) {
            boost = Math.min(MAX_BOOST, boost + GAIN_PER_TICK);
            if (dirX != 0 || dirZ != 0) {
                slideDirX = dirX;
                slideDirZ = dirZ;
            }
            slide = 0;
            slideSpeed = 0;
        } else {
            double prevBoost = boost;
            double decay = hitDecayTicks > 0 ? HIT_DECAY_PER_TICK : DECAY_PER_TICK;
            boost = Math.max(0.0D, boost - decay);

            // Sharp stop with a meaningful boost -> short inertia slide.
            boolean sharpStop = wasSprinting && !movingInput;
            if (sharpStop && prevBoost > EFFECT_THRESHOLD && slide <= 0 && hitDecayTicks == 0) {
                slide = 1.0D;
                slideSpeed = Math.max(speed, BASE_SPRINT * (1.0D + prevBoost) * 0.6D);
            }
            if (slide > 0) {
                slide -= 0.055D;
                slideSpeed *= 0.92D;
                if (slide <= 0 || slideSpeed < 0.02D) {
                    slide = 0;
                    slideSpeed = 0;
                }
            }
        }

        // Sharp camera turn while boosted: a sideways stagger + camera tilt.
        sway = 0.0D;
        targetRoll = 0.0D;
        if (sprinting && movingInput && boost > EFFECT_THRESHOLD) {
            double abs = Math.abs(yawDelta);
            if (abs > TURN_THRESHOLD) {
                double k = Math.min(1.0D, (abs - TURN_THRESHOLD) / 15.0D)
                         * (boost / MAX_BOOST);
                double sign = yawDelta > 0 ? 1.0D : -1.0D;
                sway = sign * k * 0.055D;
                targetRoll = sign * k * MAX_ROLL;
            }
        }
        roll += (targetRoll - roll) * 0.35D;
        if (Math.abs(roll) < 0.01D) roll = 0.0D;

        wasSprinting = sprinting && movingInput;
    }

    /** Target horizontal speed for this tick, or -1 when the mod should not touch movement. */
    public double targetSpeed(boolean sprinting, boolean movingInput) {
        if (boost > 0 && (sprinting || !movingInput)) {
            return Math.min(MAX_SPEED, BASE_SPRINT * (1.0D + boost));
        }
        return -1.0D;
    }

    /** Human readable speed in m/s for the HUD/debug. */
    public double metersPerSecond() {
        return BASE_SPRINT * (1.0D + boost) * 20.0D;
    }
}
