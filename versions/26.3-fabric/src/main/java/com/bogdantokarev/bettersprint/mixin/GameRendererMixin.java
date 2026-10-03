package com.bogdantokarev.bettersprint.mixin;

import com.bogdantokarev.bettersprint.BetterSprintClient;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.GameRenderer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Tilts the camera sideways on sharp turns while boosted. */
@Mixin(GameRenderer.class)
public class GameRendererMixin {

    @Inject(method = "bobView", at = @At("TAIL"))
    private void bettersprint$roll(PoseStack poseStack, float partialTick, CallbackInfo ci) {
        double roll = BetterSprintClient.ENGINE.roll;
        if (roll != 0.0D) {
            poseStack.mulPose(Axis.ZP.rotationDegrees((float) roll));
        }
    }
}
