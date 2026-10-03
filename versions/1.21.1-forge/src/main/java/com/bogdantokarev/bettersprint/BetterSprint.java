package com.bogdantokarev.bettersprint;

import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod(BetterSprint.MODID)
public class BetterSprint {
    public static final String MODID = "bettersprint";
    public static final SprintEngine ENGINE = new SprintEngine();

    public BetterSprint() {
    }

    @Mod.EventBusSubscriber(modid = MODID, value = Dist.CLIENT)
    public static class ClientEvents {

        @SubscribeEvent
        public static void onClientTick(TickEvent.ClientTickEvent event) {
            if (event.phase != TickEvent.Phase.END) return;
            Minecraft mc = Minecraft.getInstance();
            LocalPlayer p = mc.player;
            if (p == null || mc.isPaused()) return;
            if (p.getAbilities().flying || p.isInWater() || p.isPassenger() || p.isFallFlying()) {
                ENGINE.reset();
                return;
            }
        net.minecraft.world.phys.Vec3 vel = p.getDeltaMovement();
        double mx = vel.x, mz = vel.z;
        double speed = Math.sqrt(mx * mx + mz * mz);
        double dirX = speed > 1.0E-4 ? mx / speed : 0.0D;
        double dirZ = speed > 1.0E-4 ? mz / speed : 0.0D;
        boolean input = Math.abs(p.zza) > 0.01F || Math.abs(p.xxa) > 0.01F;
        boolean sprinting = p.isSprinting();

        ENGINE.tick(sprinting, input, ENGINE.yawDelta(p.getYRot()), speed, dirX, dirZ);

        double target = ENGINE.targetSpeed(sprinting, input);
        if (target > 0 && speed > 0.02D && target > speed) {
            double f = target / speed;
            mx *= f; mz *= f;
        }
        if (ENGINE.slide > 0 && !input) {
            mx = ENGINE.slideDirX * ENGINE.slideSpeed;
            mz = ENGINE.slideDirZ * ENGINE.slideSpeed;
        }
        if (ENGINE.sway != 0) {
            double yaw = Math.toRadians(p.getYRot());
            mx += ENGINE.sway * -Math.cos(yaw);
            mz += ENGINE.sway * -Math.sin(yaw);
        }
        p.setDeltaMovement(mx, vel.y, mz);
        }

        @SubscribeEvent
        public static void onAttack(AttackEntityEvent event) {
            Minecraft mc = Minecraft.getInstance();
            if (mc.player == null || event.getEntity() != mc.player) return;
            ENGINE.onAttack(!mc.player.onGround());
        }

        @SubscribeEvent
        public static void onCamera(ViewportEvent.ComputeCameraAngles event) {
            event.setRoll((float) ENGINE.roll);
        }
    }
}
