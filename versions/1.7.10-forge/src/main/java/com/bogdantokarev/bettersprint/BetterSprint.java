package com.bogdantokarev.bettersprint;

import cpw.mods.fml.common.Mod;
import cpw.mods.fml.common.event.FMLInitializationEvent;
import cpw.mods.fml.common.eventhandler.SubscribeEvent;
import cpw.mods.fml.common.gameevent.TickEvent;
import cpw.mods.fml.common.FMLCommonHandler;
import net.minecraft.client.Minecraft;
import net.minecraft.client.entity.EntityClientPlayerMP;
import net.minecraftforge.client.event.EntityViewRenderEvent;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.entity.player.AttackEntityEvent;

@Mod(modid = BetterSprint.MODID, name = BetterSprint.NAME, version = BetterSprint.VERSION)
public class BetterSprint {
    public static final String MODID = "bettersprint";
    public static final String NAME = "Better Sprint";
    public static final String VERSION = "1.0.0";

    public static final SprintEngine ENGINE = new SprintEngine();

    @Mod.EventHandler
    public void init(FMLInitializationEvent event) {
        MinecraftForge.EVENT_BUS.register(this);
        FMLCommonHandler.instance().bus().register(this);
    }

    @SubscribeEvent
    public void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getMinecraft();
        EntityClientPlayerMP p = mc.thePlayer;
        if (p == null || mc.isGamePaused()) return;
        if (p.capabilities.isFlying || p.isInWater() || p.isRiding()) { ENGINE.reset(); return; }

        double mx = p.motionX, mz = p.motionZ;
        double speed = Math.sqrt(mx * mx + mz * mz);
        double dirX = speed > 1.0E-4 ? mx / speed : 0.0D;
        double dirZ = speed > 1.0E-4 ? mz / speed : 0.0D;
        boolean input = Math.abs(p.moveForward) > 0.01F || Math.abs(p.moveStrafing) > 0.01F;
        boolean sprinting = p.isSprinting();

        ENGINE.tick(sprinting, input, ENGINE.yawDelta(p.rotationYaw), speed, dirX, dirZ);

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
            double yaw = Math.toRadians(p.rotationYaw);
            mx += ENGINE.sway * -Math.cos(yaw);
            mz += ENGINE.sway * -Math.sin(yaw);
        }
        p.motionX = mx;
        p.motionZ = mz;
    }

    @SubscribeEvent
    public void onAttack(AttackEntityEvent event) {
        Minecraft mc = Minecraft.getMinecraft();
        if (mc.thePlayer == null || event.entityPlayer != mc.thePlayer) return;
        ENGINE.onAttack(!mc.thePlayer.onGround);
    }

    @SubscribeEvent
    public void onCamera(EntityViewRenderEvent.CameraSetup event) {
        event.roll = (float) ENGINE.roll;
    }
}
