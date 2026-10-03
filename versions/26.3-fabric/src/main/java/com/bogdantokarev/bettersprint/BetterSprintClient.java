package com.bogdantokarev.bettersprint;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.event.player.AttackEntityCallback;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.phys.Vec3;

@Environment(EnvType.CLIENT)
public class BetterSprintClient implements ClientModInitializer {

    public static final SprintEngine ENGINE = new SprintEngine();

    @Override
    public void onInitializeClient() {
        ClientTickEvents.END_CLIENT_TICK.register(BetterSprintClient::tick);
        AttackEntityCallback.EVENT.register((player, world, hand, entity, hitResult) -> {
            Minecraft mc = Minecraft.getInstance();
            if (mc.player != null && player == mc.player) {
                ENGINE.onAttack(!mc.player.onGround());
            }
            return InteractionResult.PASS;
        });
    }

    private static void tick(Minecraft mc) {
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
}
