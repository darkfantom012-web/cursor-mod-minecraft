#!/usr/bin/env python3
"""Generates every loader/version port of Better Sprint from shared templates."""
import os, shutil, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "versions"
PKG = "com/bogdantokarev/bettersprint"
CORE = (ROOT / "common" / PKG / "SprintEngine.java").read_text()
ICON = (ROOT / "assets" / "icon.png").read_bytes()
MOD_VERSION = "1.0.0"
AUTHOR = "Bogdan_Tokarev"
DESC = ("Running now builds up momentum: +10% speed per second of sprinting up to 8.612 m/s, "
        "jump-friendly, with inertia slides, air-hit momentum keeping and camera tilt on sharp turns.")

def w(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)

def wb(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

# --------------------------------------------------------------------------- 1.7.10 / 1.12.2 forge
LEGACY_MAIN = """package com.bogdantokarev.bettersprint;

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
    public static final String VERSION = "%(version)s";

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
"""

MODERN_LEGACY_MAIN = """package com.bogdantokarev.bettersprint;

import net.minecraft.client.Minecraft;
import net.minecraft.client.entity.EntityPlayerSP;
import net.minecraftforge.client.event.EntityViewRenderEvent;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.common.event.FMLInitializationEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraftforge.fml.common.gameevent.TickEvent;

@Mod(modid = BetterSprint.MODID, name = BetterSprint.NAME, version = BetterSprint.VERSION,
     clientSideOnly = true, acceptableRemoteVersions = "*")
public class BetterSprint {
    public static final String MODID = "bettersprint";
    public static final String NAME = "Better Sprint";
    public static final String VERSION = "%(version)s";

    public static final SprintEngine ENGINE = new SprintEngine();

    @Mod.EventHandler
    public void init(FMLInitializationEvent event) {
        MinecraftForge.EVENT_BUS.register(this);
    }

    @SubscribeEvent
    public void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getMinecraft();
        EntityPlayerSP p = mc.player;
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
        if (mc.player == null || event.getEntityPlayer() != mc.player) return;
        ENGINE.onAttack(!mc.player.onGround);
    }

    @SubscribeEvent
    public void onCamera(EntityViewRenderEvent.CameraSetup event) {
        event.setRoll((float) ENGINE.roll);
    }
}
"""

MCMOD_INFO = """[
  {
    "modid": "bettersprint",
    "name": "Better Sprint",
    "description": "%(desc)s",
    "version": "%(version)s",
    "mcversion": "%(mc)s",
    "logoFile": "assets/bettersprint/icon.png",
    "authorList": ["%(author)s"],
    "credits": "",
    "url": "",
    "updateUrl": "",
    "parent": "",
    "screenshots": [],
    "dependencies": []
  }
]
"""

BUILD_1710 = """plugins {
    id 'com.gtnewhorizons.retrofuturagradle' version '1.3.35'
}

group = 'com.bogdantokarev'
archivesBaseName = 'BetterSprint-1.7.10-forge'
version = '%(version)s'

java {
    toolchain { languageVersion.set(JavaLanguageVersion.of(8)) }
}

minecraft {
    mcVersion = '1.7.10'
    usesFml = true
    usesForge = true
    username = 'Developer'
}

processResources {
    inputs.property 'version', project.version
    filesMatching('mcmod.info') {
        expand 'version': project.version, 'mcversion': '1.7.10'
    }
}

jar {
    manifest {
        attributes(
            'Specification-Title': 'Better Sprint',
            'Implementation-Title': 'Better Sprint',
            'Implementation-Version': project.version,
            'Implementation-Vendor': '%(author)s'
        )
    }
}
"""

BUILD_1122 = """buildscript {
    repositories {
        maven { url = 'https://maven.minecraftforge.net' }
        maven { url = 'https://repo.spongepowered.org/repository/maven-public/' }
        mavenCentral()
    }
    dependencies {
        classpath group: 'net.minecraftforge.gradle', name: 'ForgeGradle', version: '5.1.+', changing: true
    }
}

apply plugin: 'net.minecraftforge.gradle'

group = 'com.bogdantokarev'
archivesBaseName = 'BetterSprint-1.12.2-forge'
version = '%(version)s'

java {
    toolchain { languageVersion.set(JavaLanguageVersion.of(8)) }
}

minecraft {
    mappings channel: 'stable', version: '39-1.12'
}

dependencies {
    minecraft 'net.minecraftforge:forge:1.12.2-14.23.5.2860'
}

processResources {
    inputs.property 'version', project.version
    filesMatching('mcmod.info') {
        expand 'version': project.version, 'mcversion': '1.12.2'
    }
}

jar {
    manifest {
        attributes(
            'Implementation-Title': 'Better Sprint',
            'Implementation-Version': project.version,
            'Implementation-Vendor': '%(author)s'
        )
    }
}
"""

def legacy_project(name, mc, main_src, build):
    d = OUT / name
    if d.exists():
        shutil.rmtree(d)
    w(d / "src/main/java" / PKG / "SprintEngine.java", CORE)
    w(d / "src/main/java" / PKG / "BetterSprint.java", main_src % {"version": MOD_VERSION})
    w(d / "src/main/resources/mcmod.info",
      MCMOD_INFO % {"desc": DESC, "version": "${version}", "mc": "${mcversion}", "author": AUTHOR})
    wb(d / "src/main/resources/assets/bettersprint/icon.png", ICON)
    w(d / "build.gradle", build % {"version": MOD_VERSION, "author": AUTHOR})
    w(d / "settings.gradle",
      "pluginManagement {\n    repositories {\n        gradlePluginPortal()\n"
      "        maven { url = 'https://maven.minecraftforge.net' }\n"
      "        maven { url = 'https://maven.neoforged.net/releases' }\n    }\n}\n"
      "rootProject.name = 'BetterSprint-%s'\n" % name)
    w(d / "gradle.properties", "org.gradle.jvmargs=-Xmx3G\norg.gradle.daemon=false\n")

legacy_project("1.7.10-forge", "1.7.10", LEGACY_MAIN, BUILD_1710)
legacy_project("1.12.2-forge", "1.12.2", MODERN_LEGACY_MAIN, BUILD_1122)
print("legacy ok")

# --------------------------------------------------------------------------- shared modern helper
MOVEMENT_BODY = """        net.minecraft.world.phys.Vec3 vel = p.getDeltaMovement();
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
"""

FORGE_MODERN_MAIN = """package com.bogdantokarev.bettersprint;

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
            if (p.getAbilities().flying || p.isInWater() || p.isPassenger() || p.%(gliding)s) {
                ENGINE.reset();
                return;
            }
%(movement)s        }

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
"""

NEOFORGE_MAIN = """package com.bogdantokarev.bettersprint;

import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.ViewportEvent;
import net.neoforged.neoforge.event.entity.player.AttackEntityEvent;

@Mod(value = BetterSprint.MODID, dist = Dist.CLIENT)
public class BetterSprint {
    public static final String MODID = "bettersprint";
    public static final SprintEngine ENGINE = new SprintEngine();

    public BetterSprint() {
    }

    @EventBusSubscriber(modid = MODID, value = Dist.CLIENT)
    public static class ClientEvents {

        @SubscribeEvent
        public static void onClientTick(ClientTickEvent.Post event) {
            Minecraft mc = Minecraft.getInstance();
            LocalPlayer p = mc.player;
            if (p == null || mc.isPaused()) return;
            if (p.getAbilities().flying || p.isInWater() || p.isPassenger() || p.%(gliding)s) {
                ENGINE.reset();
                return;
            }
%(movement)s        }

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
"""

FABRIC_MAIN = """package com.bogdantokarev.bettersprint;

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
        if (p.getAbilities().flying || p.isInWater() || p.isPassenger() || p.%(gliding)s) {
            ENGINE.reset();
            return;
        }

%(movement)s    }
}
"""

FABRIC_MIXIN = """package com.bogdantokarev.bettersprint.mixin;

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
"""

FABRIC_MOD_JSON = """{
  "schemaVersion": 1,
  "id": "bettersprint",
  "version": "%(version)s",
  "name": "Better Sprint",
  "description": "%(desc)s",
  "authors": ["%(author)s"],
  "contact": {},
  "license": "MIT",
  "icon": "assets/bettersprint/icon.png",
  "environment": "client",
  "entrypoints": {
    "client": ["com.bogdantokarev.bettersprint.BetterSprintClient"]
  },
  "mixins": ["bettersprint.mixins.json"],
  "depends": {
    "fabricloader": ">=0.15.0",
    "minecraft": "%(mcdep)s",
    "java": ">=%(java)s",
    "fabric-api": "*"
  }
}
"""

FABRIC_MIXINS_JSON = """{
  "required": true,
  "package": "com.bogdantokarev.bettersprint.mixin",
  "compatibilityLevel": "JAVA_%(java)s",
  "client": ["GameRendererMixin"],
  "injectors": { "defaultRequire": 1 },
  "minVersion": "0.8"
}
"""

MODS_TOML = """modLoader = "%(loader)s"
loaderVersion = "%(loaderversion)s"
license = "MIT"
issueTrackerURL = ""

[[mods]]
modId = "bettersprint"
version = "%(version)s"
displayName = "Better Sprint"
authors = "%(author)s"
logoFile = "icon.png"
description = '''
%(desc)s
'''

[[dependencies.bettersprint]]
    modId = "%(depid)s"
    mandatory = true
    versionRange = "%(deprange)s"
    ordering = "NONE"
    side = "CLIENT"

[[dependencies.bettersprint]]
    modId = "minecraft"
    mandatory = true
    versionRange = "%(mcrange)s"
    ordering = "NONE"
    side = "CLIENT"
"""

PROPS = "org.gradle.jvmargs=-Xmx3G\norg.gradle.daemon=false\n"

SETTINGS = """pluginManagement {
    repositories {
        gradlePluginPortal()
        maven { url = 'https://maven.minecraftforge.net' }
        maven { url = 'https://maven.neoforged.net/releases' }
        maven { url = 'https://maven.fabricmc.net/' }
    }
}
rootProject.name = 'BetterSprint-%(name)s'
"""

BUILD_FORGE_MODERN = """plugins {
    id 'net.minecraftforge.gradle' version '[6.0.24,6.2)'
}

group = 'com.bogdantokarev'
archivesBaseName = 'BetterSprint-%(name)s'
version = '%(version)s'

java {
    toolchain { languageVersion.set(JavaLanguageVersion.of(%(java)s)) }
}

minecraft {
    mappings channel: 'official', version: '%(mc)s'
    copyIdeResources = true
    runs {
        client {
            workingDirectory project.file('run')
            mods { bettersprint { source sourceSets.main } }
        }
    }
}

dependencies {
    minecraft 'net.minecraftforge:forge:%(forge)s'
}

processResources {
    inputs.property 'version', project.version
    filesMatching('META-INF/mods.toml') { expand 'version': project.version }
}

jar {
    manifest {
        attributes(
            'Implementation-Title': 'Better Sprint',
            'Implementation-Version': project.version,
            'Implementation-Vendor': '%(author)s'
        )
    }
}
afterEvaluate {
    if (tasks.findByName('reobfJar') != null) {
        jar.finalizedBy('reobfJar')
    }
}
"""

BUILD_NEOFORGE = """plugins {
    id 'net.neoforged.moddev' version '%(mdg)s'
}

group = 'com.bogdantokarev'
version = '%(version)s'

base { archivesName = 'BetterSprint-%(name)s' }

java {
    toolchain { languageVersion.set(JavaLanguageVersion.of(%(java)s)) }
}

neoForge {
    version = '%(neoforge)s'
    runs {
        client { client() }
    }
    mods {
        bettersprint { sourceSet sourceSets.main }
    }
}

processResources {
    inputs.property 'version', project.version
    filesMatching('META-INF/neoforge.mods.toml') { expand 'version': project.version }
}

jar {
    manifest {
        attributes(
            'Implementation-Title': 'Better Sprint',
            'Implementation-Version': project.version,
            'Implementation-Vendor': '%(author)s'
        )
    }
}
"""

BUILD_FABRIC = """plugins {
    id 'fabric-loom' version '%(loom)s'
}

group = 'com.bogdantokarev'
version = '%(version)s'

base { archivesName = 'BetterSprint-%(name)s' }

java {
    toolchain { languageVersion.set(JavaLanguageVersion.of(%(java)s)) }
    withSourcesJar()
}

repositories {
    maven { url = 'https://maven.fabricmc.net/' }
}

dependencies {
    minecraft "com.mojang:minecraft:%(mc)s"
    mappings loom.officialMojangMappings()
    modImplementation "net.fabricmc:fabric-loader:%(loader)s"
    modImplementation "net.fabricmc.fabric-api:fabric-api:%(fapi)s"
}

processResources {
    inputs.property 'version', project.version
    filesMatching('fabric.mod.json') { expand 'version': project.version }
}

tasks.withType(JavaCompile).configureEach {
    it.options.release = %(java)s
}

jar {
    manifest {
        attributes(
            'Implementation-Title': 'Better Sprint',
            'Implementation-Version': project.version,
            'Implementation-Vendor': '%(author)s'
        )
    }
}
"""

def base_project(name):
    d = OUT / name
    if d.exists():
        shutil.rmtree(d)
    w(d / "src/main/java" / PKG / "SprintEngine.java", CORE)
    w(d / "settings.gradle", SETTINGS % {"name": name})
    w(d / "gradle.properties", PROPS)
    return d

def forge_modern(name, mc, forge, java, mcrange, forgerange, gliding="isFallFlying()"):
    d = base_project(name)
    w(d / "src/main/java" / PKG / "BetterSprint.java", FORGE_MODERN_MAIN % {"movement": MOVEMENT_BODY, "gliding": gliding})
    w(d / "build.gradle", BUILD_FORGE_MODERN % {"name": name, "version": MOD_VERSION, "mc": mc,
                                                "forge": forge, "java": java, "author": AUTHOR})
    w(d / "src/main/resources/META-INF/mods.toml", MODS_TOML % {
        "loader": "javafml", "loaderversion": forgerange, "version": "${version}", "author": AUTHOR,
        "desc": DESC, "depid": "forge", "deprange": forgerange, "mcrange": mcrange})
    wb(d / "src/main/resources/icon.png", ICON)
    wb(d / "src/main/resources/assets/bettersprint/icon.png", ICON)

def neoforge(name, neoforge_ver, java, mcrange, neorange, mdg="2.0.78", gliding="isFallFlying()"):
    d = base_project(name)
    w(d / "src/main/java" / PKG / "BetterSprint.java", NEOFORGE_MAIN % {"movement": MOVEMENT_BODY, "gliding": gliding})
    w(d / "build.gradle", BUILD_NEOFORGE % {"name": name, "version": MOD_VERSION,
                                            "neoforge": neoforge_ver, "java": java,
                                            "author": AUTHOR, "mdg": mdg})
    w(d / "src/main/resources/META-INF/neoforge.mods.toml", MODS_TOML % {
        "loader": "javafml", "loaderversion": "[1,)", "version": "${version}", "author": AUTHOR,
        "desc": DESC, "depid": "neoforge", "deprange": neorange, "mcrange": mcrange})
    wb(d / "src/main/resources/icon.png", ICON)
    wb(d / "src/main/resources/assets/bettersprint/icon.png", ICON)

def fabric(name, mc, yarn, loader, fapi, loom, java, mcdep, gliding="isFallFlying()"):
    d = base_project(name)
    w(d / "src/main/java" / PKG / "BetterSprintClient.java", FABRIC_MAIN % {"movement": MOVEMENT_BODY, "gliding": gliding})
    w(d / "src/main/java" / PKG / "mixin/GameRendererMixin.java", FABRIC_MIXIN)
    w(d / "build.gradle", BUILD_FABRIC % {"name": name, "version": MOD_VERSION, "mc": mc, "yarn": yarn,
                                          "loader": loader, "fapi": fapi, "loom": loom,
                                          "java": java, "author": AUTHOR})
    w(d / "src/main/resources/fabric.mod.json", FABRIC_MOD_JSON % {
        "version": "${version}", "desc": DESC, "author": AUTHOR, "mcdep": mcdep, "java": java})
    w(d / "src/main/resources/bettersprint.mixins.json", FABRIC_MIXINS_JSON % {"java": java})
    wb(d / "src/main/resources/assets/bettersprint/icon.png", ICON)

forge_modern("1.20.1-forge", "1.20.1", "1.20.1-47.3.0", 17, "[1.20.1,1.20.2)", "[47,)")
forge_modern("1.21.1-forge", "1.21.1", "1.21.1-52.0.40", 21, "[1.21.1,1.21.2)", "[52,)")

neoforge("1.21.1-neoforge", "21.1.+", 21, "[1.21.1,1.21.2)", "[21.1.0,)")
neoforge("1.21.11-neoforge", "21.11.+", 21, "[1.21.11,1.21.12)", "[21.11.0,)",
         mdg="[2.0,3.0)", gliding="isGliding()")
neoforge("26.3-neoforge", "26.3.+", 21, "[26.3,)", "[26.3.0,)",
         mdg="[2.0,3.0)", gliding="isGliding()")

fabric("1.20.1-fabric", "1.20.1", None, "0.16.9", "0.92.2+1.20.1", "1.6-SNAPSHOT", 17, ">=1.20.1")
fabric("1.21.1-fabric", "1.21.1", None, "0.16.9", "0.116.17+1.21.1", "1.7-SNAPSHOT", 21, ">=1.21.1")
fabric("1.21.11-fabric", "1.21.11", None, "0.17.2", "0.141.6+1.21.11", "1.11-SNAPSHOT", 21, ">=1.21.11",
       gliding="isGliding()")
fabric("26.3-fabric", "26.3", None, "0.19.5", "0.161.0+26.3", "1.18-SNAPSHOT", 21, ">=26.3",
       gliding="isGliding()")
print("modern ok")
