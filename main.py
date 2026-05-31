import os
import time
import math
import random
import threading
from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO, emit, disconnect
from flask_cors import CORS

html_code = r"""
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VAULT SIEGE — Wild West</title>
<link href="https://fonts.googleapis.com/css2?family=Rye&family=Special+Elite&family=Oswald:wght@400;700&display=swap" rel="stylesheet">
<script src="https://cdn.socket.io/4.8.3/socket.io.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
:root{
  --gold:#f5c842;--rust:#c0392b;--sand:#d4a843;--dark:#1a0f00;--darkbrown:#2d1a00;
  --wood:#5c3a1e;--neon-green:#39ff14;--neon-pink:#ff2d9b;--neon-blue:#00d4ff;
  --panel-bg:rgba(20,10,0,0.92);--border-gold:rgba(245,200,66,0.7);
}
body{background:#1a0f00;font-family:'Special Elite',cursive;overflow:hidden;user-select:none;}
#mainMenu{
  position:fixed;inset:0;z-index:100;
  background:radial-gradient(ellipse at center,#2d1a00 0%,#0d0600 100%);
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  transition:opacity .5s;
}
#menuCanvas{position:absolute;inset:0;pointer-events:none;}
.menu-inner{position:relative;z-index:2;text-align:center;width:480px;}
.menu-title{
  font-family:'Rye',cursive;font-size:52px;color:var(--gold);
  text-shadow:0 0 20px rgba(245,200,66,.8),0 0 40px rgba(245,200,66,.4),2px 2px 0 #8b4513;
  margin-bottom:8px;line-height:1.1;letter-spacing:3px;
  animation:titlePulse 2s ease-in-out infinite;
}
.menu-sub{font-family:'Oswald',sans-serif;font-size:18px;color:#d4a843;letter-spacing:6px;margin-bottom:40px;opacity:.8;}
@keyframes titlePulse{0%,100%{text-shadow:0 0 20px rgba(245,200,66,.8),0 0 40px rgba(245,200,66,.4),2px 2px 0 #8b4513;}50%{text-shadow:0 0 30px rgba(245,200,66,1),0 0 60px rgba(245,200,66,.6),2px 2px 0 #8b4513;}}
.menu-panel{
  background:var(--panel-bg);border:2px solid var(--border-gold);border-radius:4px;
  padding:30px 36px;box-shadow:0 0 30px rgba(245,200,66,.2),inset 0 0 20px rgba(0,0,0,.5);
}
.menu-panel::before{content:'';position:absolute;top:-2px;left:20px;right:20px;height:2px;background:linear-gradient(90deg,transparent,var(--gold),transparent);}
.input-group{margin-bottom:18px;text-align:left;}
.input-group label{display:block;font-size:13px;color:var(--sand);letter-spacing:2px;margin-bottom:6px;text-transform:uppercase;}
.input-group input{
  width:100%;background:rgba(0,0,0,.5);border:1px solid rgba(245,200,66,.4);
  border-radius:3px;padding:10px 14px;color:#f5c842;font-family:'Special Elite',cursive;font-size:15px;
  outline:none;transition:border-color .3s,box-shadow .3s;
}
.input-group input:focus{border-color:var(--gold);box-shadow:0 0 10px rgba(245,200,66,.3);}
.input-group input::placeholder{color:rgba(212,168,67,.4);}
.btn{
  display:block;width:100%;padding:13px;margin-bottom:12px;cursor:pointer;
  font-family:'Rye',cursive;font-size:16px;letter-spacing:2px;
  border:2px solid;border-radius:3px;transition:all .2s;position:relative;overflow:hidden;
}
.btn::before{content:'';position:absolute;inset:0;background:rgba(255,255,255,.05);transform:translateX(-100%);transition:transform .3s;}
.btn:hover::before{transform:translateX(0);}
.btn-solo{color:#1a0f00;background:linear-gradient(135deg,#f5c842,#c8942a);border-color:#f5c842;box-shadow:0 0 15px rgba(245,200,66,.3);}
.btn-solo:hover{box-shadow:0 0 25px rgba(245,200,66,.6);transform:translateY(-1px);}
.btn-mp{color:var(--neon-blue);background:rgba(0,212,255,.1);border-color:var(--neon-blue);box-shadow:0 0 12px rgba(0,212,255,.2);}
.btn-mp:hover{background:rgba(0,212,255,.2);box-shadow:0 0 25px rgba(0,212,255,.4);transform:translateY(-1px);}
.divider{display:flex;align-items:center;gap:12px;margin:16px 0;}
.divider span{color:rgba(212,168,67,.5);font-size:12px;letter-spacing:2px;}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(245,200,66,.3),transparent);}
.status-msg{font-size:12px;text-align:center;margin-top:8px;min-height:18px;color:#ff6b6b;letter-spacing:1px;}
.status-msg.ok{color:var(--neon-green);}

#gameContainer{position:fixed;inset:0;display:none;}
#gameCanvas{display:block;}
#hud{position:fixed;top:0;left:0;right:0;height:64px;pointer-events:none;z-index:10;}
.hud-box{
  position:absolute;background:rgba(20,10,0,.85);border:1px solid rgba(245,200,66,.5);
  border-radius:3px;padding:6px 14px;font-family:'Oswald',sans-serif;
  box-shadow:0 0 10px rgba(0,0,0,.5);
}
#hudLeft{left:12px;top:10px;min-width:200px;}
#hudMid{top:10px;left:50%;transform:translateX(-50%);min-width:220px;text-align:center;}
#hudRight{right:12px;top:10px;min-width:160px;text-align:right;}
.hud-label{font-size:10px;color:var(--sand);letter-spacing:2px;text-transform:uppercase;}
.hud-val{font-size:20px;color:var(--gold);font-weight:700;}
.hud-val.danger{color:#ff4444;animation:blink .5s infinite;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:.4;}}
.bar-wrap{width:160px;height:8px;background:rgba(0,0,0,.6);border-radius:4px;border:1px solid rgba(255,255,255,.1);overflow:hidden;margin-top:4px;}
.bar-fill{height:100%;border-radius:4px;transition:width .3s;}
.bar-hp{background:linear-gradient(90deg,#ff4444,#ff8800);}
.bar-safe{background:linear-gradient(90deg,#f5c842,#39ff14);}
#effectDisplay{position:fixed;bottom:80px;left:12px;z-index:10;}
.effect-chip{
  display:inline-flex;align-items:center;gap:8px;background:rgba(20,10,0,.9);
  border:1px solid var(--border-gold);border-radius:3px;padding:6px 12px;
  font-family:'Oswald',sans-serif;font-size:13px;color:var(--gold);margin-bottom:4px;
  animation:fadeInLeft .3s ease;
}
@keyframes fadeInLeft{from{transform:translateX(-20px);opacity:0;}to{transform:translateX(0);opacity:1;}}
.effect-timer{color:rgba(245,200,66,.6);font-size:11px;}
#waveNotif{
  position:fixed;top:80px;left:50%;transform:translateX(-50%);
  font-family:'Rye',cursive;font-size:28px;color:var(--gold);
  text-shadow:0 0 20px rgba(245,200,66,.8);z-index:20;pointer-events:none;
  opacity:0;transition:opacity .5s;text-align:center;
}
#crosshair{position:fixed;pointer-events:none;z-index:5;display:none;}
#chatBox{position:fixed;bottom:10px;left:12px;width:280px;z-index:10;}
#chatMessages{
  max-height:80px;overflow:hidden;display:flex;flex-direction:column-reverse;gap:2px;margin-bottom:4px;
}
.chat-line{font-family:'Oswald',sans-serif;font-size:12px;padding:2px 6px;background:rgba(0,0,0,.5);border-radius:2px;color:#e0c97f;}
#chatInput{
  width:100%;background:rgba(20,10,0,.85);border:1px solid rgba(245,200,66,.3);
  border-radius:2px;padding:5px 8px;color:var(--gold);font-family:'Special Elite',cursive;font-size:12px;
  outline:none;display:none;
}
#minimap{position:fixed;bottom:10px;right:12px;z-index:10;border:1px solid rgba(245,200,66,.4);background:rgba(0,0,0,.7);}

/* Modal */
.modal-overlay{
  position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:50;
  display:flex;align-items:center;justify-content:center;
  opacity:0;pointer-events:none;transition:opacity .3s;
}
.modal-overlay.open{opacity:1;pointer-events:all;}
.modal{
  background:var(--panel-bg);border:2px solid var(--border-gold);border-radius:4px;
  width:520px;max-width:95vw;max-height:85vh;overflow-y:auto;
  box-shadow:0 0 40px rgba(245,200,66,.3),0 0 80px rgba(0,0,0,.8);
  transform:scale(.95);transition:transform .3s;
  scrollbar-width:thin;scrollbar-color:rgba(245,200,66,.3) transparent;
}
.modal-overlay.open .modal{transform:scale(1);}
.modal-header{
  padding:16px 20px;border-bottom:1px solid rgba(245,200,66,.3);
  font-family:'Rye',cursive;font-size:20px;color:var(--gold);
  display:flex;justify-content:space-between;align-items:center;
  background:linear-gradient(90deg,rgba(245,200,66,.1),transparent);
}
.modal-close{cursor:pointer;color:rgba(245,200,66,.5);font-size:22px;transition:color .2s;line-height:1;}
.modal-close:hover{color:var(--gold);}
.modal-body{padding:16px 20px;}
.modal-money{font-family:'Oswald',sans-serif;font-size:14px;color:var(--gold);padding:8px 20px;border-bottom:1px solid rgba(245,200,66,.15);}
.shop-section{margin-bottom:20px;}
.shop-section h3{font-family:'Oswald',sans-serif;font-size:13px;letter-spacing:3px;color:var(--sand);text-transform:uppercase;margin-bottom:10px;border-bottom:1px solid rgba(212,168,67,.2);padding-bottom:4px;}
.shop-item{
  display:flex;align-items:center;justify-content:space-between;
  padding:8px 10px;margin-bottom:6px;background:rgba(255,255,255,.04);
  border:1px solid rgba(245,200,66,.15);border-radius:3px;transition:background .2s;
}
.shop-item:hover{background:rgba(245,200,66,.07);}
.item-info{flex:1;}
.item-name{font-family:'Oswald',sans-serif;font-size:14px;color:#e0c97f;}
.item-desc{font-size:11px;color:rgba(212,168,67,.6);margin-top:2px;}
.item-equipped{font-size:10px;color:var(--neon-green);margin-top:2px;}
.btn-buy{
  padding:6px 14px;font-family:'Oswald',sans-serif;font-size:13px;font-weight:700;
  border:1px solid;border-radius:2px;cursor:pointer;transition:all .2s;white-space:nowrap;
}
.btn-buy-gold{color:#1a0f00;background:var(--gold);border-color:var(--gold);}
.btn-buy-gold:hover:not(:disabled){box-shadow:0 0 12px rgba(245,200,66,.5);}
.btn-buy:disabled{opacity:.4;cursor:not-allowed;}
.upgrade-row{display:flex;gap:4px;margin-top:4px;}
.btn-upgrade{padding:3px 8px;font-size:10px;font-family:'Oswald',sans-serif;border:1px solid rgba(245,200,66,.4);background:rgba(245,200,66,.1);color:var(--sand);border-radius:2px;cursor:pointer;transition:all .2s;}
.btn-upgrade:hover:not(:disabled){background:rgba(245,200,66,.2);}
.btn-upgrade:disabled{opacity:.35;cursor:not-allowed;}

/* Gambler */
.gambler-btn{
  display:block;width:100%;padding:20px;margin:10px 0;
  font-family:'Rye',cursive;font-size:18px;cursor:pointer;
  background:linear-gradient(135deg,rgba(255,45,155,.15),rgba(100,0,150,.15));
  border:2px solid var(--neon-pink);color:var(--neon-pink);border-radius:4px;
  box-shadow:0 0 15px rgba(255,45,155,.2);transition:all .3s;
  position:relative;overflow:hidden;
}
.gambler-btn:hover{box-shadow:0 0 30px rgba(255,45,155,.5);transform:scale(1.02);}
.gambler-btn:disabled{opacity:.5;cursor:not-allowed;transform:none;}
.effect-result{
  text-align:center;padding:16px;border-radius:3px;margin-top:10px;
  font-family:'Oswald',sans-serif;font-size:18px;font-weight:700;
  animation:popIn .4s cubic-bezier(.68,-.55,.265,1.55);
}
@keyframes popIn{from{transform:scale(0.5);opacity:0;}to{transform:scale(1);opacity:1;}}
.effect-pos{color:var(--neon-green);background:rgba(57,255,20,.1);border:1px solid rgba(57,255,20,.3);}
.effect-neg{color:#ff4444;background:rgba(255,68,68,.1);border:1px solid rgba(255,68,68,.3);}

/* Game Over */
#gameOver{
  position:fixed;inset:0;z-index:80;display:none;align-items:center;justify-content:center;
  background:rgba(0,0,0,.85);
}
#gameOver .panel{
  background:var(--panel-bg);border:2px solid var(--rust);border-radius:4px;
  padding:40px;text-align:center;min-width:380px;
  box-shadow:0 0 60px rgba(192,57,43,.4);animation:popIn .5s cubic-bezier(.68,-.55,.265,1.55);
}
#gameOver h1{font-family:'Rye',cursive;font-size:42px;color:var(--rust);text-shadow:0 0 20px rgba(192,57,43,.6);margin-bottom:12px;}
#gameOver .stats{color:var(--sand);font-family:'Oswald',sans-serif;font-size:16px;margin:20px 0;line-height:2;}
#gameOver .stat-val{color:var(--gold);font-size:22px;font-weight:700;}

/* Floating numbers */
.float-num{
  position:fixed;pointer-events:none;z-index:30;font-family:'Oswald',sans-serif;font-weight:700;
  animation:floatUp 1.2s ease forwards;white-space:nowrap;
}
@keyframes floatUp{0%{transform:translateY(0);opacity:1;}100%{transform:translateY(-60px);opacity:0;}}

/* Players list */
#playersList{position:fixed;top:80px;right:12px;z-index:10;}
.player-entry{
  background:rgba(20,10,0,.8);border:1px solid rgba(245,200,66,.3);border-radius:2px;
  padding:4px 10px;margin-bottom:3px;font-family:'Oswald',sans-serif;font-size:12px;
  display:flex;align-items:center;gap:6px;
}
.player-dot{width:8px;height:8px;border-radius:50%;}

/* Respawn counter */
#respawnMsg{
  position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);z-index:25;
  font-family:'Rye',cursive;font-size:32px;color:#ff4444;text-align:center;
  text-shadow:0 0 20px rgba(255,68,68,.6);display:none;pointer-events:none;
}

/* Wave breather */
#waveBreather{
  position:fixed;bottom:100px;left:50%;transform:translateX(-50%);z-index:20;
  background:rgba(20,10,0,.9);border:2px solid var(--gold);border-radius:4px;
  padding:10px 24px;font-family:'Rye',cursive;font-size:16px;color:var(--gold);
  text-align:center;display:none;box-shadow:0 0 20px rgba(245,200,66,.3);
}
</style>
</head>
<body>

<!-- MAIN MENU -->
<div id="mainMenu">
  <canvas id="menuCanvas"></canvas>
  <div class="menu-inner">
    <div class="menu-title">VAULT<br>SIEGE</div>
    <div class="menu-sub">★ WILD WEST ★</div>
    <div class="menu-panel" style="position:relative;">
      <div class="input-group">
        <label>Ваш псевдоним</label>
        <input id="nickInput" type="text" placeholder="Ковбой Билл" maxlength="16" value="Cowboy">
      </div>
      <button class="btn btn-solo" onclick="startSolo()">🤠 Одиночная игра</button>
      <div class="divider"><span>МУЛЬТИПЛЕЕР</span></div>
      <div class="input-group">
        <label>Адрес сервера</label>
        <input id="serverAddr" type="text" placeholder="https://xxxx.ngrok.io" value="">
      </div>
      <button class="btn btn-mp" onclick="connectMP()">🌐 Подключиться к серверу</button>
      <div class="status-msg" id="statusMsg"></div>
    </div>
  </div>
</div>

<!-- GAME CONTAINER -->
<div id="gameContainer">
  <canvas id="gameCanvas"></canvas>

  <!-- HUD -->
  <div id="hud">
    <div class="hud-box" id="hudLeft">
      <div class="hud-label">Здоровье</div>
      <div class="hud-val" id="hudHp">100</div>
      <div class="bar-wrap"><div class="bar-fill bar-hp" id="barHp" style="width:100%"></div></div>
    </div>
    <div class="hud-box" id="hudMid">
      <div class="hud-label">⬡ СЕЙФ</div>
      <div class="hud-val" id="hudSafe">1000</div>
      <div class="bar-wrap" style="width:180px;margin:4px auto 0;"><div class="bar-fill bar-safe" id="barSafe" style="width:100%"></div></div>
    </div>
    <div class="hud-box" id="hudRight">
      <div class="hud-label">💰 Деньги</div>
      <div class="hud-val" id="hudMoney">$0</div>
      <div style="margin-top:4px;font-family:'Oswald',sans-serif;font-size:12px;color:var(--sand);" id="hudWave">Волна 1</div>
      <div style="font-size:11px;color:rgba(212,168,67,.6);" id="hudWeapon">Пистолет</div>
    </div>
  </div>

  <div id="effectDisplay"></div>
  <div id="waveNotif"></div>
  <div id="waveBreather">Следующая волна через: <span id="breatherCount">10</span>с — Посетите автомат!</div>
  <div id="chatBox">
    <div id="chatMessages"></div>
    <input id="chatInput" type="text" placeholder="Чат (Enter — отправить)..." maxlength="80">
  </div>
  <canvas id="minimap" width="140" height="100"></canvas>
  <div id="playersList"></div>
  <div id="respawnMsg">☠️ ВЫБЫВАЕТЕ...<br><span id="respawnCount">5</span>с</div>
</div>

<!-- SHOP MODAL (Vending Machine) -->
<div class="modal-overlay" id="shopModal">
  <div class="modal">
    <div class="modal-header">
      <span>🛒 Продовольственный Магазин</span>
      <span class="modal-close" onclick="closeShop()">✕</span>
    </div>
    <div class="modal-money">💰 Ваши деньги: $<span id="shopMoney">0</span></div>
    <div class="modal-body" id="shopBody"></div>
  </div>
</div>

<!-- GAMBLER MODAL -->
<div class="modal-overlay" id="gamblerModal">
  <div class="modal" style="border-color:var(--neon-pink);box-shadow:0 0 40px rgba(255,45,155,.3);">
    <div class="modal-header" style="border-bottom-color:rgba(255,45,155,.3);background:linear-gradient(90deg,rgba(255,45,155,.1),transparent);">
      <span style="color:var(--neon-pink);">🎰 Колесо Фортуны</span>
      <span class="modal-close" onclick="closeGambler()">✕</span>
    </div>
    <div class="modal-money">💰 Ваши деньги: $<span id="gamblerMoney">0</span></div>
    <div class="modal-body">
      <div style="text-align:center;color:rgba(212,168,67,.7);font-family:'Oswald',sans-serif;font-size:13px;margin-bottom:12px;">
        Попытайте удачу, ковбой!<br>Стоимость: <strong style="color:var(--neon-pink);">$50</strong> — эффект 25 сек.
      </div>
      <div id="activeEffectInfo" style="margin-bottom:10px;display:none;padding:8px 12px;background:rgba(255,255,255,.05);border-radius:3px;font-family:'Oswald',sans-serif;font-size:13px;color:var(--sand);">
        Активный эффект: <span id="activeEffectName" style="color:var(--gold);"></span> — <span id="activeEffectTime"></span>с
      </div>
      <button class="gambler-btn" id="gamblerBtn" onclick="doGamble()">🎲 КРУТИТЬ БАРАБАН ($50)</button>
      <div id="gamblerResult"></div>
    </div>
  </div>
</div>

<!-- GAME OVER -->
<div id="gameOver" style="display:none;flex-direction:column;">
  <div class="panel">
    <h1>☠️ ОГРАБЛЕН!</h1>
    <p style="color:var(--sand);font-family:'Oswald',sans-serif;">Сейф взломан. Бандиты победили.</p>
    <div class="stats" id="goStats"></div>
    <button class="btn btn-solo" style="margin-top:10px;" onclick="restartGame()">🔄 Играть снова</button>
    <button class="btn btn-mp" style="margin-top:8px;" onclick="goToMenu()">🏠 Главное меню</button>
  </div>
</div>

<script>
// ============================================================
// VAULT SIEGE — Wild West | Client v1.0
// ============================================================

// ─── CONSTANTS ───────────────────────────────────────────────
const WORLD_W = 1200, WORLD_H = 840;
const SAFE_X = WORLD_W/2, SAFE_Y = WORLD_H/2;
const SAFE_W = 72, SAFE_H = 80;
const PLAYER_R = 14, PLAYER_SPEED = 2.8;
const BULLET_SPEED = 9;
const INTERACT_DIST = 90;
const VEND_X = WORLD_W/2 - 130, VEND_Y = WORLD_H/2 - 10;
const GAMB_X = WORLD_W/2 + 130, GAMB_Y = WORLD_H/2 - 10;
const ENEMY_TYPES = ['grunt','runner','heavy','shooter','bomber'];
const PLAYER_COLORS = ['#f5c842','#39ff14','#00d4ff','#ff2d9b','#ff8c00','#bf5fff'];
const WEAPONS = {
  pistol:{name:'Пистолет',damage:22,fireRate:420,bulletSpeed:9,spread:0.06,ammo:Infinity,maxAmmo:Infinity,reloadTime:0,pierce:false,price:0,color:'#aaa'},
  shotgun:{name:'Дробовик',damage:30,fireRate:900,bulletSpeed:8,spread:0.35,pellets:6,ammo:40,maxAmmo:40,reloadTime:1800,price:120,color:'#c0392b'},
  rifle:{name:'Автомат',damage:14,fireRate:110,bulletSpeed:10,spread:0.08,ammo:90,maxAmmo:90,reloadTime:2200,price:180,color:'#27ae60'},
  sniper:{name:'Снайпер',damage:90,fireRate:1800,bulletSpeed:16,spread:0.01,ammo:15,maxAmmo:15,reloadTime:2600,price:250,color:'#8e44ad'},
};
const EFFECTS = [
  {id:'dmg_up',name:'+30% Урон',icon:'⚔️',positive:true,color:'#39ff14'},
  {id:'spd_up',name:'+50% Скорость',icon:'💨',positive:true,color:'#00d4ff'},
  {id:'inf_ammo',name:'Беск. патроны',icon:'♾️',positive:true,color:'#f5c842'},
  {id:'regen',name:'Регенерация',icon:'💚',positive:true,color:'#2ecc71'},
  {id:'shield',name:'Щит',icon:'🛡️',positive:true,color:'#3498db'},
  {id:'slow',name:'Замедление',icon:'🐢',positive:false,color:'#e74c3c'},
  {id:'invert',name:'Инверсия упр.',icon:'🌀',positive:false,color:'#9b59b6'},
  {id:'dmg_down',name:'-50% Урон',icon:'💔',positive:false,color:'#e67e22'},
  {id:'money_drain',name:'Утечка денег',icon:'💸',positive:false,color:'#c0392b'},
  {id:'drunk',name:'Пьяное прицел.',icon:'🥴',positive:false,color:'#d35400'},
];
const TURRET_PRICE = 300, TURRET_RATE = 800, TURRET_RANGE = 200, TURRET_DMG = 18;

// ─── STATE ────────────────────────────────────────────────────
let canvas, ctx, miniCtx;
let gameMode = null; // 'solo' | 'mp'
let socket = null;
let animId = null;
let lastTime = 0, deltaTime = 0;

let localPlayer = null;
let players = {}; // id → player
let bullets = []; // client-side
let enemies = [];
let particles = [];
let floatNums = [];
let turrets = [];
let drops = [];
let obstacles = [];

let safeHP = 1000, safeMaxHP = 1000, safeLevel = 1;
let wave = 0, waveActive = false, waveBreather = false, breatherTimer = 0;
let gameOver = false;
let waveEnemyCount = 0, waveKilled = 0;
let totalKills = 0;
let myId = null;
let nickname = 'Cowboy';
let shopOpen = false, gamblerOpen = false;
let respawning = false, respawnTimer = 0;
let activeEffect = null, effectTimer = 0;
let waveNotifTimer = 0;
let chatActive = false;
let mpEnemyId = 0;

// ─── INPUT ────────────────────────────────────────────────────
let keys = {};
let mouse = {x:0,y:0,wx:0,wy:0,down:false};
let camX = 0, camY = 0;

// ─── MENU PARTICLES ──────────────────────────────────────────
let menuCanvas, menuCtx, menuParticles = [], menuAnimId;
function initMenuParticles(){
  menuCanvas = document.getElementById('menuCanvas');
  menuCtx = menuCanvas.getContext('2d');
  menuCanvas.width = window.innerWidth;
  menuCanvas.height = window.innerHeight;
  for(let i=0;i<60;i++){
    menuParticles.push({
      x:Math.random()*menuCanvas.width, y:Math.random()*menuCanvas.height,
      vx:(Math.random()-.5)*.4, vy:(Math.random()-.5)*.4,
      r:Math.random()*2+.5, a:Math.random(),
      color:['#f5c842','#c0392b','#d4a843','#8b4513'][Math.floor(Math.random()*4)]
    });
  }
  animMenu();
}
function animMenu(){
  menuAnimId = requestAnimationFrame(animMenu);
  menuCtx.clearRect(0,0,menuCanvas.width,menuCanvas.height);
  menuParticles.forEach(p=>{
    p.x+=p.vx; p.y+=p.vy;
    if(p.x<0)p.x=menuCanvas.width;
    if(p.x>menuCanvas.width)p.x=0;
    if(p.y<0)p.y=menuCanvas.height;
    if(p.y>menuCanvas.height)p.y=0;
    menuCtx.beginPath();
    menuCtx.arc(p.x,p.y,p.r,0,Math.PI*2);
    menuCtx.fillStyle=p.color;
    menuCtx.globalAlpha=p.a*0.7;
    menuCtx.fill();
    menuCtx.globalAlpha=1;
  });
  // draw stars
  menuCtx.fillStyle='rgba(245,200,66,0.15)';
  for(let i=0;i<5;i++){
    let cx=menuCanvas.width*.15+i*menuCanvas.width*.17;
    let cy=menuCanvas.height*.85;
    drawStar(menuCtx,cx,cy,4,18,8);
  }
}
function drawStar(c,cx,cy,n,or,ir){
  c.beginPath();
  for(let i=0;i<n*2;i++){
    let a=Math.PI*i/n - Math.PI/2;
    let r=i%2===0?or:ir;
    i===0?c.moveTo(cx+Math.cos(a)*r,cy+Math.sin(a)*r):c.lineTo(cx+Math.cos(a)*r,cy+Math.sin(a)*r);
  }
  c.closePath();c.fill();
}

// ─── START SOLO ───────────────────────────────────────────────
function startSolo(){
  nickname = document.getElementById('nickInput').value.trim() || 'Cowboy';
  cancelAnimationFrame(menuAnimId);
  document.getElementById('mainMenu').style.opacity='0';
  setTimeout(()=>{document.getElementById('mainMenu').style.display='none';},500);
  gameMode='solo';
  initGame();
}

// ─── CONNECT MULTIPLAYER ──────────────────────────────────────
function connectMP(){
  let addr = document.getElementById('serverAddr').value.trim();
  if(!addr){setStatus('Введите адрес сервера!',false);return;}
  nickname = document.getElementById('nickInput').value.trim() || 'Cowboy';
  setStatus('Подключение...','info');
  try{
    socket = io(addr,{transports:['websocket','polling'],timeout:8000});
    socket.on('connect',()=>{
      socket.emit('join',{nick:nickname});
      setStatus('Подключено! Ожидание...','ok');
    });
    socket.on('init',data=>{
      myId = data.id;
      cancelAnimationFrame(menuAnimId);
      document.getElementById('mainMenu').style.opacity='0';
      setTimeout(()=>{document.getElementById('mainMenu').style.display='none';},500);
      gameMode='mp';
      // Load server state
      safeHP = data.safeHP; safeMaxHP = data.safeMaxHP; safeLevel = data.safeLevel||1;
      wave = data.wave; waveActive = data.waveActive;
      // Create local player from data
      let pd = data.players[myId];
      if(!pd){setStatus('Ошибка: нет данных игрока',false);return;}
      initGame(data);
    });
    socket.on('connect_error',()=>setStatus('Ошибка подключения!',false));
    socket.on('disconnect',()=>{if(gameMode==='mp'){showGameOver(true);}});
    setupSocketListeners();
  }catch(e){setStatus('Ошибка: '+e.message,false);}
}

function setStatus(msg,ok){
  let el=document.getElementById('statusMsg');
  el.textContent=msg;
  el.className='status-msg'+(ok==='ok'?' ok':ok===false?' ':'');
}

// ─── SOCKET LISTENERS ─────────────────────────────────────────
function setupSocketListeners(){
  if(!socket) return;
  socket.on('state_update', data=>{
    // Update remote players
    for(let id in data.players){
      if(id===myId) continue;
      if(!players[id]){
        players[id]=createRemotePlayer(id,data.players[id]);
      } else {
        let p=players[id];
        p.tx=data.players[id].x; p.ty=data.players[id].y;
        p.angle=data.players[id].angle||0;
        p.hp=data.players[id].hp;
        p.nick=data.players[id].nick;
        p.weaponKey=data.players[id].weapon||'pistol';
        p.dead=data.players[id].dead||false;
      }
    }
    // Remove disconnected
    for(let id in players){
      if(id!==myId && !data.players[id]) delete players[id];
    }
    // Safe
    safeHP=data.safeHP; safeMaxHP=data.safeMaxHP; safeLevel=data.safeLevel||1;
    // Wave
    wave=data.wave; waveActive=data.waveActive;
    if(data.waveBreather!==undefined) waveBreather=data.waveBreather;
    // Enemies
    enemies=data.enemies||[];
    // Turrets
    turrets=data.turrets||[];
    if(data.gameOver) showGameOver(false);
  });
  socket.on('enemy_hit',data=>{
    spawnFloat(data.x,data.y,'-'+data.dmg,data.killed?'#f5c842':'#ff4444');
    if(data.killed){
      totalKills++;
      if(data.moneyReward) localPlayer.money+=data.moneyReward;
      spawnParticles(data.x,data.y,10,'#f5c842');
    }
  });
  socket.on('player_hit',data=>{
    if(data.id===myId){
      localPlayer.hp=data.hp;
      if(localPlayer.hp<=0) startRespawn();
    }
  });
  socket.on('safe_hit',data=>{
    safeHP=data.hp;
    spawnFloat(SAFE_X,SAFE_Y-40,'-'+data.dmg,'#ff4444');
    spawnParticles(SAFE_X,SAFE_Y,8,'#ff4444');
  });
  socket.on('wave_start',data=>{
    wave=data.wave;
    waveActive=true; waveBreather=false;
    showWaveNotif('★ Волна '+wave+' ★');
  });
  socket.on('wave_end',()=>{
    waveActive=false; waveBreather=true;
    breatherTimer=15;
    showWaveBreather();
  });
  socket.on('chat_msg',data=>{
    addChat(data.nick+': '+data.text);
  });
  socket.on('effect_applied',data=>{
    if(data.id===myId){
      let eff=EFFECTS.find(e=>e.id===data.effectId);
      if(eff){activeEffect={...eff};effectTimer=25;renderEffectDisplay();}
    }
  });
  socket.on('buy_result',data=>{
    if(data.ok){
      localPlayer.money=data.money;
      if(data.hp) localPlayer.hp=data.hp;
      if(data.weapon) localPlayer.weaponKey=data.weapon;
    }
  });
}

// ─── INIT GAME ────────────────────────────────────────────────
function initGame(serverData){
  canvas=document.getElementById('gameCanvas');
  ctx=canvas.getContext('2d');
  canvas.width=window.innerWidth;
  canvas.height=window.innerHeight;
  document.getElementById('gameContainer').style.display='block';

  miniCtx=document.getElementById('minimap').getContext('2d');

  // Build obstacles
  buildObstacles();

  // Create local player
  myId = myId || 'solo_'+Date.now();
  let colorIdx = Object.keys(players).length;
  localPlayer = {
    id:myId, nick:nickname,
    x:SAFE_X, y:SAFE_Y+120,
    tx:SAFE_X, ty:SAFE_Y+120,
    vx:0, vy:0,
    hp:100, maxHp:100,
    money:0,
    angle:0,
    weaponKey:'pistol',
    weapons:{'pistol':{...WEAPONS.pistol,curAmmo:Infinity,reloading:false}},
    lastFire:0,
    color:PLAYER_COLORS[colorIdx%PLAYER_COLORS.length],
    dead:false,
    shield:false,
    kills:0,
  };
  players[myId]=localPlayer;

  if(serverData){
    // Restore money etc from server
    let pd=serverData.players[myId];
    if(pd){
      localPlayer.x=pd.x||SAFE_X;
      localPlayer.y=pd.y||SAFE_Y+120;
      localPlayer.money=pd.money||0;
    }
  }

  // Input listeners
  setupInput();

  // Start game loop
  if(animId) cancelAnimationFrame(animId);
  lastTime=performance.now();
  gameOver=false;
  document.getElementById('gameOver').style.display='none';

  if(gameMode==='solo'){
    // Start wave 1
    wave=0;
    startNextWave();
  }

  gameLoop(performance.now());
  updatePlayersList();
}

// ─── OBSTACLES ────────────────────────────────────────────────
function buildObstacles(){
  obstacles=[];
  let defs=[
    // Barrels clusters
    {x:180,y:180,w:40,h:40,type:'barrel'},
    {x:230,y:180,w:40,h:40,type:'barrel'},
    {x:180,y:230,w:40,h:40,type:'barrel'},
    // Crates
    {x:WORLD_W-200,y:180,w:55,h:55,type:'crate'},
    {x:WORLD_W-145,y:180,w:55,h:55,type:'crate'},
    {x:180,y:WORLD_H-220,w:55,h:55,type:'crate'},
    {x:240,y:WORLD_H-220,w:55,h:55,type:'crate'},
    {x:WORLD_W-200,y:WORLD_H-220,w:55,h:55,type:'crate'},
    // Wagons
    {x:WORLD_W/2-240,y:160,w:100,h:50,type:'wagon'},
    {x:WORLD_W/2+140,y:160,w:100,h:50,type:'wagon'},
    {x:WORLD_W/2-240,y:WORLD_H-210,w:100,h:50,type:'wagon'},
    {x:WORLD_W/2+140,y:WORLD_H-210,w:100,h:50,type:'wagon'},
    // Side walls (partial)
    {x:0,y:WORLD_H/2-80,w:60,h:160,type:'wall'},
    {x:WORLD_W-60,y:WORLD_H/2-80,w:60,h:160,type:'wall'},
    // Corner rocks
    {x:100,y:WORLD_H/2-30,w:40,h:60,type:'rock'},
    {x:WORLD_W-140,y:WORLD_H/2-30,w:40,h:60,type:'rock'},
    {x:WORLD_W/2-30,y:100,w:60,h:40,type:'rock'},
    {x:WORLD_W/2-30,y:WORLD_H-140,w:60,h:40,type:'rock'},
  ];
  obstacles=defs;
}

// ─── INPUT SETUP ──────────────────────────────────────────────
function setupInput(){
  document.addEventListener('keydown',onKeyDown);
  document.addEventListener('keyup',e=>{keys[e.code]=false;});
  canvas.addEventListener('mousemove',onMouseMove);
  canvas.addEventListener('mousedown',e=>{if(e.button===0&&!shopOpen&&!gamblerOpen&&!chatActive)mouse.down=true;});
  canvas.addEventListener('mouseup',e=>{if(e.button===0)mouse.down=false;});
  canvas.addEventListener('contextmenu',e=>e.preventDefault());

  document.getElementById('chatInput').addEventListener('keydown',e=>{
    if(e.key==='Enter'){
      let msg=document.getElementById('chatInput').value.trim();
      if(msg){
        if(gameMode==='mp'&&socket) socket.emit('chat',{text:msg});
        else addChat(localPlayer.nick+': '+msg);
        document.getElementById('chatInput').value='';
      }
      document.getElementById('chatInput').style.display='none';
      chatActive=false;
      canvas.focus();
    }
    if(e.key==='Escape'){
      document.getElementById('chatInput').style.display='none';
      chatActive=false;
    }
    e.stopPropagation();
  });
}

function onKeyDown(e){
  if(chatActive){return;}
  keys[e.code]=true;
  if(e.code==='KeyE') tryInteract();
  if(e.code==='KeyT'&&gameMode==='mp'){
    document.getElementById('chatInput').style.display='block';
    document.getElementById('chatInput').focus();
    chatActive=true;
  }
  if(e.code==='KeyR') tryReload();
  if(e.key>='1'&&e.key<='4'){
    let wk=['pistol','shotgun','rifle','sniper'][+e.key-1];
    if(localPlayer&&localPlayer.weapons[wk]) localPlayer.weaponKey=wk;
  }
}

function onMouseMove(e){
  mouse.x=e.clientX; mouse.y=e.clientY;
  mouse.wx=e.clientX+camX; mouse.wy=e.clientY+camY;
}

function tryReload(){
  if(!localPlayer||localPlayer.dead) return;
  let w=localPlayer.weapons[localPlayer.weaponKey];
  if(!w||w.maxAmmo===Infinity||w.reloading) return;
  w.reloading=true;
  setTimeout(()=>{if(w){w.curAmmo=w.maxAmmo;w.reloading=false;}},w.reloadTime);
}

// ─── INTERACTIONS ─────────────────────────────────────────────
function tryInteract(){
  if(!localPlayer||localPlayer.dead||gameOver) return;
  let dx1=localPlayer.x-VEND_X, dy1=localPlayer.y-VEND_Y;
  if(Math.sqrt(dx1*dx1+dy1*dy1)<INTERACT_DIST){openShop();return;}
  let dx2=localPlayer.x-GAMB_X, dy2=localPlayer.y-GAMB_Y;
  if(Math.sqrt(dx2*dx2+dy2*dy2)<INTERACT_DIST){openGambler();return;}
}

// ─── SHOP ─────────────────────────────────────────────────────
function openShop(){
  shopOpen=true;
  renderShop();
  document.getElementById('shopModal').classList.add('open');
}
function closeShop(){
  shopOpen=false;
  document.getElementById('shopModal').classList.remove('open');
}

function renderShop(){
  document.getElementById('shopMoney').textContent=localPlayer.money;
  let body=document.getElementById('shopBody');
  let m=localPlayer.money;
  let p=localPlayer;
  let safeRepairCost=Math.max(1,Math.floor((safeMaxHP-safeHP)*0.6));
  let safeUpgCost=200+safeLevel*100;
  let healCost=30;

  body.innerHTML=`
  <div class="shop-section">
    <h3>🏦 Сейф (HP: ${Math.ceil(safeHP)}/${safeMaxHP})</h3>
    <div class="shop-item">
      <div class="item-info">
        <div class="item-name">Починить сейф</div>
        <div class="item-desc">Восстановить до максимума</div>
      </div>
      <button class="btn-buy btn-buy-gold" onclick="buyRepairSafe()" ${m<safeRepairCost||safeHP>=safeMaxHP?'disabled':''}>$${safeRepairCost}</button>
    </div>
    <div class="shop-item">
      <div class="item-info">
        <div class="item-name">Улучшить сейф (ур. ${safeLevel})</div>
        <div class="item-desc">+200 максимального HP</div>
      </div>
      <button class="btn-buy btn-buy-gold" onclick="buyUpgradeSafe()" ${m<safeUpgCost?'disabled':''}>$${safeUpgCost}</button>
    </div>
  </div>
  <div class="shop-section">
    <h3>❤️ Лечение (HP: ${p.hp}/${p.maxHp})</h3>
    <div class="shop-item">
      <div class="item-info">
        <div class="item-name">Аптечка</div>
        <div class="item-desc">Восстановить 50 HP</div>
      </div>
      <button class="btn-buy btn-buy-gold" onclick="buyHeal(50,${healCost})" ${m<healCost||p.hp>=p.maxHp?'disabled':''}>$${healCost}</button>
    </div>
    <div class="shop-item">
      <div class="item-info">
        <div class="item-name">Полное лечение</div>
        <div class="item-desc">Восстановить всё HP</div>
      </div>
      <button class="btn-buy btn-buy-gold" onclick="buyHeal(100,80)" ${m<80||p.hp>=p.maxHp?'disabled':''}>$80</button>
    </div>
  </div>
  <div class="shop-section">
    <h3>🔫 Оружие</h3>
    ${Object.entries(WEAPONS).map(([k,w])=>`
    <div class="shop-item">
      <div class="item-info">
        <div class="item-name">${w.name}</div>
        <div class="item-desc">Урон: ${w.damage} | Скор: ${w.fireRate}мс | ${w.ammo===Infinity?'∞ патр.':w.maxAmmo+' патр.'}</div>
        ${p.weapons[k]?`<div class="item-equipped">${p.weaponKey===k?'✓ АКТИВНО':'✓ Куплено'}</div>`:''}
        ${p.weapons[k]?renderUpgrades(k):''}
      </div>
      ${!p.weapons[k]?`<button class="btn-buy btn-buy-gold" onclick="buyWeapon('${k}')" ${m<w.price||k==='pistol'?'disabled':''}>$${w.price}</button>`
      :`<button class="btn-buy" style="color:var(--neon-green);border-color:var(--neon-green);background:rgba(57,255,20,.1);" onclick="equipWeapon('${k}')">Взять</button>`}
    </div>`).join('')}
  </div>
  <div class="shop-section">
    <h3>🏗️ Турель ($${TURRET_PRICE})</h3>
    <div class="shop-item">
      <div class="item-info">
        <div class="item-name">Установить турель</div>
        <div class="item-desc">Авто-стрельба по врагам, радиус ${TURRET_RANGE}px, урон ${TURRET_DMG}</div>
        <div class="item-desc">Турелей на карте: ${turrets.length}</div>
      </div>
      <button class="btn-buy btn-buy-gold" onclick="buyTurret()" ${m<TURRET_PRICE?'disabled':''}>$${TURRET_PRICE}</button>
    </div>
  </div>`;
}

function renderUpgrades(k){
  let p=localPlayer;
  if(!p.weapons[k]) return '';
  let upgLevel=(p.weaponUpgrades||{})[k]||0;
  let upgCost=80+upgLevel*60;
  return `<div class="upgrade-row">
    <button class="btn-upgrade" onclick="buyWeaponUpgrade('${k}')" ${p.money<upgCost||upgLevel>=5?'disabled':''}>⬆ Улучш. (ур.${upgLevel}) $${upgCost}</button>
  </div>`;
}

function buyRepairSafe(){
  let cost=Math.floor((safeMaxHP-safeHP)*0.6);
  if(localPlayer.money<cost||safeHP>=safeMaxHP) return;
  localPlayer.money-=cost;
  if(gameMode==='mp') socket.emit('buy',{type:'repair_safe',cost});
  else {safeHP=safeMaxHP; spawnFloat(SAFE_X,SAFE_Y-50,'ПОЧИНЕН!','#39ff14');}
  renderShop();
}
function buyUpgradeSafe(){
  let cost=200+safeLevel*100;
  if(localPlayer.money<cost) return;
  localPlayer.money-=cost;
  if(gameMode==='mp') socket.emit('buy',{type:'upgrade_safe',cost});
  else {safeLevel++;safeMaxHP+=200;safeHP=Math.min(safeHP+200,safeMaxHP);spawnFloat(SAFE_X,SAFE_Y-50,'СЕЙФ УЛ.!','#39ff14');}
  renderShop();
}
function buyHeal(amount,cost){
  if(localPlayer.money<cost||localPlayer.hp>=localPlayer.maxHp) return;
  localPlayer.money-=cost;
  if(gameMode==='mp') socket.emit('buy',{type:'heal',amount,cost});
  else {localPlayer.hp=Math.min(localPlayer.hp+amount,localPlayer.maxHp);}
  renderShop();
}
function buyWeapon(k){
  let w=WEAPONS[k];
  if(!w||localPlayer.weapons[k]) return;
  if(localPlayer.money<w.price) return;
  localPlayer.money-=w.price;
  localPlayer.weapons[k]={...w,curAmmo:w.maxAmmo===Infinity?Infinity:w.maxAmmo,reloading:false};
  localPlayer.weaponKey=k;
  if(gameMode==='mp') socket.emit('buy',{type:'weapon',weaponKey:k,cost:w.price});
  renderShop();
}
function equipWeapon(k){
  if(localPlayer.weapons[k]) localPlayer.weaponKey=k;
  renderShop();
}
function buyWeaponUpgrade(k){
  if(!localPlayer.weapons[k]) return;
  if(!localPlayer.weaponUpgrades) localPlayer.weaponUpgrades={};
  let lvl=(localPlayer.weaponUpgrades[k]||0);
  let cost=80+lvl*60;
  if(localPlayer.money<cost||lvl>=5) return;
  localPlayer.money-=cost;
  localPlayer.weaponUpgrades[k]=lvl+1;
  // Apply upgrade
  let w=localPlayer.weapons[k];
  w.damage=Math.floor(w.damage*1.15);
  w.fireRate=Math.max(50,Math.floor(w.fireRate*0.92));
  if(w.maxAmmo!==Infinity) w.maxAmmo=Math.floor(w.maxAmmo*1.1);
  if(gameMode==='mp') socket.emit('buy',{type:'weapon_upgrade',weaponKey:k,cost});
  renderShop();
}
function buyTurret(){
  if(localPlayer.money<TURRET_PRICE) return;
  localPlayer.money-=TURRET_PRICE;
  let angle=Math.random()*Math.PI*2;
  let tx=localPlayer.x+Math.cos(angle)*60;
  let ty=localPlayer.y+Math.sin(angle)*60;
  tx=Math.max(40,Math.min(WORLD_W-40,tx));
  ty=Math.max(40,Math.min(WORLD_H-40,ty));
  if(gameMode==='mp') socket.emit('buy',{type:'turret',x:tx,y:ty,cost:TURRET_PRICE});
  else turrets.push({id:'t'+Date.now(),x:tx,y:ty,lastFire:0,hp:80,maxHp:80});
  renderShop();
}

// ─── GAMBLER ──────────────────────────────────────────────────
function openGambler(){
  gamblerOpen=true;
  document.getElementById('gamblerMoney').textContent=localPlayer.money;
  let btn=document.getElementById('gamblerBtn');
  btn.disabled=localPlayer.money<50;
  let aiEl=document.getElementById('activeEffectInfo');
  if(activeEffect){
    aiEl.style.display='block';
    document.getElementById('activeEffectName').textContent=activeEffect.icon+' '+activeEffect.name;
    document.getElementById('activeEffectTime').textContent=Math.ceil(effectTimer);
  } else {aiEl.style.display='none';}
  document.getElementById('gamblerResult').innerHTML='';
  document.getElementById('gamblerModal').classList.add('open');
}
function closeGambler(){
  gamblerOpen=false;
  document.getElementById('gamblerModal').classList.remove('open');
}
function doGamble(){
  if(localPlayer.money<50) return;
  localPlayer.money-=50;
  document.getElementById('gamblerMoney').textContent=localPlayer.money;
  let eff=EFFECTS[Math.floor(Math.random()*EFFECTS.length)];
  if(gameMode==='mp') socket.emit('gamble');
  else applyEffect(eff);
  let res=document.getElementById('gamblerResult');
  res.innerHTML=`<div class="effect-result ${eff.positive?'effect-pos':'effect-neg'}">${eff.icon} ${eff.name}</div>`;
  document.getElementById('gamblerBtn').disabled=localPlayer.money<50;
}
function applyEffect(eff){
  activeEffect={...eff};
  effectTimer=25;
  renderEffectDisplay();
  spawnFloat(localPlayer.x,localPlayer.y-30,eff.icon+' '+eff.name,eff.positive?'#39ff14':'#ff4444');
}

function renderEffectDisplay(){
  let el=document.getElementById('effectDisplay');
  if(!activeEffect){el.innerHTML='';return;}
  el.innerHTML=`<div class="effect-chip" style="border-color:${activeEffect.color};">
    ${activeEffect.icon} ${activeEffect.name}
    <span class="effect-timer">${Math.ceil(effectTimer)}с</span>
  </div>`;
}

// ─── WAVE MANAGEMENT (SOLO) ────────────────────────────────────
function startNextWave(){
  if(gameOver) return;
  wave++;
  waveActive=true; waveBreather=false;
  enemies=[];
  pendingSpawns=0;
  document.getElementById('waveBreather').style.display='none';
  let baseCount=5+wave*3;
  let bossWave=(wave%5===0);
  waveEnemyCount=baseCount+(bossWave?1:0);
  waveKilled=0;
  showWaveNotif('★ Волна '+wave+' ★'+(bossWave?' [БОСС]':''));
  // Spawn enemies over time
  spawnWaveEnemies(baseCount,bossWave);
}

let pendingSpawns=0;
function spawnWaveEnemies(count,bossWave){
  pendingSpawns=count+(bossWave?1:0);
  for(let i=0;i<count;i++){
    let d=i*Math.max(200,800-wave*20);
    setTimeout(()=>{
      if(!waveActive||gameOver){pendingSpawns=Math.max(0,pendingSpawns-1);return;}
      let type=chooseEnemyType(wave,false);
      spawnEnemy(type,false);
      pendingSpawns=Math.max(0,pendingSpawns-1);
    },d);
  }
  if(bossWave){
    setTimeout(()=>{
      if(!waveActive||gameOver){pendingSpawns=Math.max(0,pendingSpawns-1);return;}
      spawnEnemy('boss',true);
      pendingSpawns=Math.max(0,pendingSpawns-1);
    },count*300+1000);
  }
}

function chooseEnemyType(w,boss){
  let pool=['grunt'];
  if(w>=2) pool.push('runner');
  if(w>=3) pool.push('heavy');
  if(w>=4) pool.push('shooter');
  if(w>=5) pool.push('bomber');
  return pool[Math.floor(Math.random()*pool.length)];
}

function getSpawnPos(){
  let side=Math.floor(Math.random()*4);
  let x,y,margin=30;
  if(side===0){x=Math.random()*WORLD_W;y=margin;}
  else if(side===1){x=WORLD_W-margin;y=Math.random()*WORLD_H;}
  else if(side===2){x=Math.random()*WORLD_W;y=WORLD_H-margin;}
  else{x=margin;y=Math.random()*WORLD_H;}
  return {x,y};
}

function spawnEnemy(type,isBoss){
  let pos=getSpawnPos();
  let base={
    id:'e'+(++mpEnemyId),
    x:pos.x,y:pos.y,
    type:type,
    isBoss:isBoss,
    state:'move',
    lastAttack:0,
    lastShot:0,
    vx:0,vy:0,
    shield:false,shieldHp:0,
    abilities:[],
    abilityTimer:0,
    slowAura:false,
  };
  // Type stats
  let stats=getEnemyStats(type,wave,isBoss);
  Object.assign(base,stats);
  enemies.push(base);
}

function getEnemyStats(type,w,isBoss){
  let wm=1+wave*0.12;
  if(type==='boss'||isBoss){
    // Random abilities pool
    let pool=['minions','shield','regen','slow_aura','teleport','ranged_attack'];
    let abils=[];
    let num=2+Math.floor(wave/5);
    for(let i=0;i<Math.min(num,4);i++){
      let a=pool[Math.floor(Math.random()*pool.length)];
      if(!abils.includes(a)) abils.push(a);
    }
    return {hp:Math.floor(800*wm),maxHp:Math.floor(800*wm),speed:1.0*wm,damage:35*wm,reward:200,
            radius:28,color:'#ff2200',abilities:abils,attackRange:50,attackRate:1800,shootRange:280,shootRate:2000};
  }
  let s={
    grunt:{hp:Math.floor(60*wm),maxHp:Math.floor(60*wm),speed:1.4*wm,damage:12*wm,reward:20,radius:13,color:'#c0392b',attackRange:30,attackRate:1000,shootRange:0,shootRate:9999},
    runner:{hp:Math.floor(30*wm),maxHp:Math.floor(30*wm),speed:2.8*wm,damage:8*wm,reward:12,radius:11,color:'#e67e22',attackRange:25,attackRate:800,shootRange:0,shootRate:9999},
    heavy:{hp:Math.floor(180*wm),maxHp:Math.floor(180*wm),speed:0.8*wm,damage:30*wm,reward:40,radius:20,color:'#8e44ad',attackRange:35,attackRate:2000,shootRange:0,shootRate:9999},
    shooter:{hp:Math.floor(50*wm),maxHp:Math.floor(50*wm),speed:1.2*wm,damage:10*wm,reward:25,radius:12,color:'#3498db',attackRange:30,attackRate:1500,shootRange:260,shootRate:1200},
    bomber:{hp:Math.floor(40*wm),maxHp:Math.floor(40*wm),speed:1.8*wm,damage:50*wm,reward:30,radius:14,color:'#f39c12',attackRange:40,attackRate:9999,shootRange:0,shootRate:9999},
  }[type];
  if(!s) return {hp:60,maxHp:60,speed:1.4,damage:12,reward:20,radius:13,color:'#c0392b',attackRange:30,attackRate:1000,shootRange:0,shootRate:9999};
  return s;
}

// ─── GAME LOOP ────────────────────────────────────────────────
function gameLoop(ts){
  animId=requestAnimationFrame(gameLoop);
  deltaTime=Math.min((ts-lastTime)/1000,0.1);
  lastTime=ts;
  if(!gameOver){
    update(deltaTime);
  }
  render();
}

function update(dt){
  if(!localPlayer) return;
  updateCamera();
  updatePlayer(dt);
  if(gameMode==='solo'){
    updateEnemies(dt);
    updateTurrets(dt);
    updateDrops(dt);
    checkWaveEnd();
    updateBreather(dt);
  }
  updateBullets(dt);
  updateParticles(dt);
  updateFloatNums();
  updateEffect(dt);
  updateRespawn(dt);
  updateWaveNotif();
  updateHUD();
  updatePlayersList();
}

function updateCamera(){
  if(!localPlayer) return;
  let tx=localPlayer.x-canvas.width/2;
  let ty=localPlayer.y-canvas.height/2;
  tx=Math.max(0,Math.min(WORLD_W-canvas.width,tx));
  ty=Math.max(0,Math.min(WORLD_H-canvas.height,ty));
  camX+=(tx-camX)*0.1;
  camY+=(ty-camY)*0.1;
  // If world smaller than screen
  if(WORLD_W<=canvas.width) camX=(WORLD_W-canvas.width)/2;
  if(WORLD_H<=canvas.height) camY=(WORLD_H-canvas.height)/2;
}

function updatePlayer(dt){
  if(respawning||localPlayer.dead) return;
  let p=localPlayer;

  // Aim
  let wx=mouse.x+camX, wy=mouse.y+camY;
  p.angle=Math.atan2(wy-p.y,wx-p.x);

  // Movement
  let spd=PLAYER_SPEED*(hasEffect('spd_up')?1.5:1)*(hasEffect('slow')?0.7:1)*(p._auraSlowed?0.6:1);
  let dx=0,dy=0;
  let inv=hasEffect('invert');
  if(keys['KeyW']||keys['ArrowUp'])    {dy+=(inv?1:-1);}
  if(keys['KeyS']||keys['ArrowDown'])  {dy+=(inv?-1:1);}
  if(keys['KeyA']||keys['ArrowLeft'])  {dx+=(inv?1:-1);}
  if(keys['KeyD']||keys['ArrowRight']) {dx+=(inv?-1:1);}
  if(dx!==0&&dy!==0){dx*=0.707;dy*=0.707;}
  let nx=p.x+dx*spd*60*dt, ny=p.y+dy*spd*60*dt;
  nx=Math.max(PLAYER_R,Math.min(WORLD_W-PLAYER_R,nx));
  ny=Math.max(PLAYER_R,Math.min(WORLD_H-PLAYER_R,ny));
  // Obstacle collision
  let {rx,ry}=resolveObstacleCollision(nx,ny,PLAYER_R);
  p.x=rx; p.y=ry;

  // Shooting
  if(mouse.down&&!shopOpen&&!gamblerOpen){
    tryShoot();
  }

  // Effects
  if(hasEffect('regen')){
    p.hp=Math.min(p.maxHp,p.hp+10*dt);
  }
  if(hasEffect('money_drain')){
    p.money=Math.max(0,p.money-5*dt);
  }

  // Send to server
  if(gameMode==='mp'){
    socket.emit('move',{x:p.x,y:p.y,angle:p.angle,weapon:p.weaponKey});
  }
}

function resolveObstacleCollision(nx,ny,r){
  for(let o of obstacles){
    // Expand rect by radius
    let ex=o.x-r, ey=o.y-r, ew=o.w+r*2, eh=o.h+r*2;
    if(nx>ex&&nx<ex+ew&&ny>ey&&ny<ey+eh){
      // Push out on shortest axis
      let overL=nx-(ex);
      let overR=(ex+ew)-nx;
      let overT=ny-(ey);
      let overB=(ey+eh)-ny;
      let minO=Math.min(overL,overR,overT,overB);
      if(minO===overL) nx=ex;
      else if(minO===overR) nx=ex+ew;
      else if(minO===overT) ny=ey;
      else ny=ey+eh;
    }
  }
  return {rx:nx,ry:ny};
}

function tryShoot(){
  let p=localPlayer;
  let wk=p.weaponKey;
  let wDef=WEAPONS[wk];
  let wInst=p.weapons[wk];
  if(!wDef||!wInst) return;
  let now=Date.now();
  if(now-p.lastFire<wDef.fireRate) return;
  if(wInst.reloading) return;
  let hasInf=hasEffect('inf_ammo');
  if(!hasInf&&wInst.maxAmmo!==Infinity&&wInst.curAmmo<=0){
    tryReload(); return;
  }
  p.lastFire=now;
  if(!hasInf&&wInst.maxAmmo!==Infinity) wInst.curAmmo--;

  let dmgMult=(hasEffect('dmg_up')?1.3:1)*(hasEffect('dmg_down')?0.5:1);
  let angle=p.angle;
  if(hasEffect('drunk')) angle+=( Math.random()-.5)*0.5;

  let pellets=wDef.pellets||1;
  let spreadBase=wDef.spread||0;
  for(let i=0;i<pellets;i++){
    let a=angle+(Math.random()-.5)*spreadBase*2;
    if(pellets>1) a=angle+(i/(pellets-1)-0.5)*spreadBase*2;
    let b={
      x:p.x+Math.cos(a)*PLAYER_R,
      y:p.y+Math.sin(a)*PLAYER_R,
      vx:Math.cos(a)*wDef.bulletSpeed,
      vy:Math.sin(a)*wDef.bulletSpeed,
      damage:Math.floor(wDef.damage*dmgMult),
      owner:'player',
      color:wDef.color||'#f5c842',
      r:wk==='sniper'?4:2.5,
      life:1.0,
      pierce:wDef.pierce||false,
    };
    bullets.push(b);
    if(gameMode==='mp') socket.emit('shoot',{x:b.x,y:b.y,vx:b.vx,vy:b.vy,damage:b.damage,weaponKey:wk});
    spawnParticles(b.x,b.y,3,'#ffee88',3);
  }
}

function updateBullets(dt){
  for(let i=bullets.length-1;i>=0;i--){
    let b=bullets[i];
    b.x+=b.vx*60*dt;
    b.y+=b.vy*60*dt;
    b.life-=dt*1.2;
    // Check world bounds
    if(b.x<0||b.x>WORLD_W||b.y<0||b.y>WORLD_H||b.life<=0){
      bullets.splice(i,1); continue;
    }
    // Check obstacles
    let hit=false;
    for(let o of obstacles){
      if(b.x>o.x&&b.x<o.x+o.w&&b.y>o.y&&b.y<o.y+o.h){
        spawnParticles(b.x,b.y,4,'#aaa',4);
        bullets.splice(i,1); hit=true; break;
      }
    }
    if(hit) continue;
    // Solo: check enemy hits
    if(gameMode==='solo'&&b.owner==='player'){
      let hitAny=false;
      for(let j=0;j<enemies.length;j++){
        let e=enemies[j];
        if(e.dead) continue;
        let dx=b.x-e.x,dy=b.y-e.y;
        if(dx*dx+dy*dy<(e.radius+2)*(e.radius+2)){
          hitEnemy(e,b.damage);
          hitAny=true;
          if(!b.pierce){bullets.splice(i,1);hit=true;}
          break;
        }
      }
      if(hitAny&&hit) continue;
    }
    // Enemy bullets hit player
    if(b.owner==='enemy'&&!respawning&&!localPlayer.dead){
      let p=localPlayer;
      let dx=b.x-p.x,dy=b.y-p.y;
      if(dx*dx+dy*dy<PLAYER_R*PLAYER_R){
        if(p.shield){p.shield=false;spawnFloat(p.x,p.y-20,'ЩИТБЛ!','#3498db');}
        else{
          p.hp-=b.damage;
          spawnFloat(p.x,p.y-20,'-'+Math.round(b.damage),'#ff4444');
        }
        bullets.splice(i,1);
        if(p.hp<=0) startRespawn();
      }
    }
  }
}

function hitEnemy(e,dmg){
  if(e.dead) return;
  if(e.shield){
    e.shieldHp=(e.shieldHp||0)-dmg;
    if(e.shieldHp<=0){e.shield=false;spawnFloat(e.x,e.y-20,'ЩИТ!','#3498db');}
    spawnFloat(e.x,e.y-20,'-'+dmg,'#3498db');
    return;
  }
  e.hp-=dmg;
  spawnFloat(e.x,e.y-20,'-'+dmg,'#ff4444');
  spawnParticles(e.x,e.y,5,'#c0392b',5);
  if(e.hp<=0&&!e.dead){
    e.dead=true;
    waveKilled++;
    totalKills++;
    let reward=e.reward||20;
    localPlayer.money+=reward;
    spawnFloat(e.x,e.y-36,'+$'+reward,'#f5c842');
    spawnParticles(e.x,e.y,12,e.color,8);
    // Drop
    if(Math.random()<0.25) spawnDrop(e.x,e.y);
    // Bomber explode
    if(e.type==='bomber'){
      explosionDamage(e.x,e.y,80,50);
    }
  }
}

function explosionDamage(x,y,r,dmg){
  spawnParticles(x,y,20,'#f39c12',12);
  spawnFloat(x,y-20,'💥','#f39c12');
  // Damage enemies in radius
  enemies.forEach(e=>{
    if(e.dead) return;
    let dx=e.x-x,dy=e.y-y;
    if(dx*dx+dy*dy<r*r){
      e.hp-=dmg;
      if(e.hp<=0){e.dead=true;waveKilled++;totalKills++;localPlayer.money+=e.reward;
        spawnFloat(e.x,e.y-20,'+$'+e.reward,'#f5c842');
        spawnParticles(e.x,e.y,10,e.color,8);}
    }
  });
  // Damage safe if close
  let ds=Math.sqrt((x-SAFE_X)*(x-SAFE_X)+(y-SAFE_Y)*(y-SAFE_Y));
  if(ds<120){safeHP=Math.max(0,safeHP-dmg*0.5);if(safeHP<=0)triggerGameOver();}
  // Damage player
  if(!respawning){
    let dp=Math.sqrt((x-localPlayer.x)*(x-localPlayer.x)+(y-localPlayer.y)*(y-localPlayer.y));
    if(dp<r){
      localPlayer.hp-=dmg*0.7;
      if(localPlayer.hp<=0) startRespawn();
    }
  }
}

function updateEnemies(dt){
  let now=Date.now();
  for(let i=enemies.length-1;i>=0;i--){
    let e=enemies[i];
    if(e.dead){enemies.splice(i,1);continue;}
    // Boss abilities
    if(e.isBoss) updateBossAbilities(e,now,dt);
    // Find target (safe or player)
    let target=findTarget(e);
    // Shooter: keep distance
    if(e.type==='shooter'||e.isBoss){
      let dist=Math.sqrt((e.x-target.x)**2+(e.y-target.y)**2);
      if(e.type==='shooter'&&dist>120&&dist<e.shootRange){
        // Stay in range, strafe
        let angle=Math.atan2(target.y-e.y,target.x-e.x);
        e.x+=Math.cos(angle)*e.speed*0.5*60*dt;
        e.y+=Math.sin(angle)*e.speed*0.5*60*dt;
      } else if(dist>e.shootRange||e.isBoss){
        moveToward(e,target.x,target.y,dt);
      }
    } else {
      moveToward(e,target.x,target.y,dt);
    }
    // Clamp
    e.x=Math.max(e.radius,Math.min(WORLD_W-e.radius,e.x));
    e.y=Math.max(e.radius,Math.min(WORLD_H-e.radius,e.y));
    // Grunt: dash at low HP
    if(e.type==='grunt'&&e.hp<e.maxHp*0.3&&Math.random()<0.002) e.speed=Math.min(e.speed*1.5,4);
    // Attack
    let dSafe=Math.sqrt((e.x-SAFE_X)**2+(e.y-SAFE_Y)**2);
    let safeEdge=(SAFE_W/2+SAFE_H/2)/2+e.radius;
    if(dSafe<safeEdge+e.attackRange){
      if(now-e.lastAttack>e.attackRate){
        e.lastAttack=now;
        let dmg=e.damage;
        safeHP=Math.max(0,safeHP-dmg);
        spawnFloat(SAFE_X,SAFE_Y-40,'-'+Math.round(dmg),'#ff4444');
        spawnParticles(SAFE_X,SAFE_Y,6,'#ff4444',6);
        if(safeHP<=0) triggerGameOver();
        if(e.type==='bomber'){
          explosionDamage(e.x,e.y,80,e.damage);
          e.dead=true; waveKilled++;totalKills++;localPlayer.money+=e.reward;
          spawnFloat(e.x,e.y-20,'+$'+e.reward,'#f5c842');
          enemies.splice(i,1); continue;
        }
      }
    }
    // Shooter attack player
    if(e.type==='shooter'||e.isBoss){
      let dPl=Math.sqrt((e.x-localPlayer.x)**2+(e.y-localPlayer.y)**2);
      if(dPl<(e.shootRange||260)&&now-e.lastShot>e.shootRate){
        e.lastShot=now;
        let angle=Math.atan2(localPlayer.y-e.y,localPlayer.x-e.x);
        bullets.push({
          x:e.x,y:e.y,
          vx:Math.cos(angle)*(e.isBoss?9:7),
          vy:Math.sin(angle)*(e.isBoss?9:7),
          damage:e.isBoss?Math.floor(e.damage*0.4):Math.floor(e.damage),
          owner:'enemy',color:'#ff2200',r:3,life:1.2,pierce:false
        });
      }
    }
    // Slow aura — apply temporary slow effect to local player
    if(e.slowAura&&!activeEffect){
      let dPl=Math.sqrt((e.x-localPlayer.x)**2+(e.y-localPlayer.y)**2);
      if(dPl<180){
        // Temporarily reduce speed via a pseudo-effect
        if(!e._slowNotified){e._slowNotified=true;spawnFloat(localPlayer.x,localPlayer.y-30,'⚗ ЗАМЕДЛЕНИЕ','#8e44ad');}
        // We track aura slow separately
        localPlayer._auraSlowed=true;
      } else {localPlayer._auraSlowed=false;}
    }
  }
  // Reset aura slow if no slow-aura boss nearby
  if(localPlayer){
    let anyAura=enemies.some(e=>e.slowAura&&!e.dead&&Math.sqrt((e.x-localPlayer.x)**2+(e.y-localPlayer.y)**2)<180);
    if(!anyAura) localPlayer._auraSlowed=false;
  }
}

function updateBossAbilities(e,now,dt){
  if(!e.abilityTimer) e.abilityTimer=now;
  if(now-e.abilityTimer>8000){
    e.abilityTimer=now;
    let ab=e.abilities[Math.floor(Math.random()*e.abilities.length)];
    if(!ab) return;
    if(ab==='minions'){
      for(let i=0;i<3;i++){
        let ne=getEnemyStats('grunt',wave,false);
        let angle=Math.random()*Math.PI*2;
        enemies.push({...ne,id:'e'+(++mpEnemyId),
          x:e.x+Math.cos(angle)*60,y:e.y+Math.sin(angle)*60,
          isBoss:false,state:'move',lastAttack:0,lastShot:0,abilities:[]});
      }
      spawnFloat(e.x,e.y-40,'Призыв!','#ff2200');
    }
    if(ab==='teleport'){
      let pos=getSpawnPos();
      e.x=pos.x; e.y=pos.y;
      spawnParticles(e.x,e.y,15,'#9b59b6',10);
      spawnFloat(e.x,e.y-40,'ТелеПорт!','#9b59b6');
    }
    if(ab==='shield'){
      e.shield=true; e.shieldHp=300;
      spawnFloat(e.x,e.y-40,'ЩИТБОССА!','#3498db');
    }
    if(ab==='regen'){
      e.hp=Math.min(e.maxHp,e.hp+e.maxHp*0.2);
      spawnFloat(e.x,e.y-40,'РЕГЕН!','#2ecc71');
    }
    if(ab==='slow_aura'){
      e.slowAura=true;
      spawnFloat(e.x,e.y-40,'АУРА!','#8e44ad');
    }
    if(ab==='ranged_attack'){
      for(let i=0;i<8;i++){
        let ang=Math.PI*2*i/8;
        bullets.push({x:e.x,y:e.y,vx:Math.cos(ang)*8,vy:Math.sin(ang)*8,
          damage:Math.floor(e.damage*0.6),owner:'enemy',color:'#ff6600',r:4,life:1.4,pierce:false});
      }
    }
  }
}

function findTarget(e){
  // Find nearest player or default to safe
  let best={x:SAFE_X,y:SAFE_Y};
  let bestD=Infinity;
  for(let id in players){
    let p=players[id];
    if(p.dead||respawning&&id===myId) continue;
    let d=(p.x-e.x)**2+(p.y-e.y)**2;
    if(d<bestD){bestD=d;best=p;}
  }
  // Prefer safe if nearby
  let dSafe=(SAFE_X-e.x)**2+(SAFE_Y-e.y)**2;
  if(dSafe<(e.type==='bomber'||e.type==='heavy'?90000:160000)) return {x:SAFE_X,y:SAFE_Y};
  return best;
}

function moveToward(e,tx,ty,dt){
  let dx=tx-e.x,dy=ty-e.y;
  let d=Math.sqrt(dx*dx+dy*dy);
  if(d<2) return;
  let spd=e.speed;
  // Apply boss slow aura check
  for(let en of enemies){if(en.slowAura&&en!==e){let ds=(en.x-e.x)**2+(en.y-e.y)**2;if(ds<15000){/*only player slowed*/}}}
  e.x+=dx/d*spd*60*dt;
  e.y+=dy/d*spd*60*dt;
}

function updateTurrets(dt){
  let now=Date.now();
  turrets.forEach(t=>{
    // Find nearest enemy
    let nearest=null,nearD=Infinity;
    enemies.forEach(e=>{
      if(e.dead) return;
      let d=(e.x-t.x)**2+(e.y-t.y)**2;
      if(d<TURRET_RANGE*TURRET_RANGE&&d<nearD){nearD=d;nearest=e;}
    });
    if(nearest&&now-t.lastFire>TURRET_RATE){
      t.lastFire=now;
      let angle=Math.atan2(nearest.y-t.y,nearest.x-t.x);
      bullets.push({x:t.x,y:t.y,vx:Math.cos(angle)*8,vy:Math.sin(angle)*8,
        damage:TURRET_DMG,owner:'player',color:'#39ff14',r:2.5,life:1.0,pierce:false});
    }
  });
}

function updateDrops(dt){
  for(let i=drops.length-1;i>=0;i--){
    let d=drops[i];
    d.life-=dt;
    if(d.life<=0){drops.splice(i,1);continue;}
    // Check pickup
    if(!localPlayer.dead&&!respawning){
      let dx=d.x-localPlayer.x,dy=d.y-localPlayer.y;
      if(dx*dx+dy*dy<(PLAYER_R+12)**2){
        if(d.type==='hp') {localPlayer.hp=Math.min(localPlayer.maxHp,localPlayer.hp+30);spawnFloat(d.x,d.y-20,'+30 HP','#2ecc71');}
        if(d.type==='money') {localPlayer.money+=d.amount;spawnFloat(d.x,d.y-20,'+$'+d.amount,'#f5c842');}
        if(d.type==='ammo'){
          let wk=localPlayer.weaponKey;
          let wi=localPlayer.weapons[wk];
          if(wi&&wi.maxAmmo!==Infinity){wi.curAmmo=Math.min(wi.maxAmmo,wi.curAmmo+20);spawnFloat(d.x,d.y-20,'+20 патр.','#00d4ff');}
        }
        drops.splice(i,1);
      }
    }
  }
}

function spawnDrop(x,y){
  let r=Math.random();
  let type=r<0.4?'hp':r<0.7?'money':'ammo';
  drops.push({x,y,type,amount:type==='money'?Math.floor(Math.random()*15+5):0,life:12});
}

function checkWaveEnd(){
  if(!waveActive||waveBreather||gameOver) return;
  // Clean dead enemies
  enemies=enemies.filter(e=>!e.dead);
  if(enemies.length===0&&waveKilled>0&&pendingSpawns===0){
    waveActive=false;
    waveBreather=true;
    breatherTimer=10;
    showWaveBreather();
  }
}

function showWaveBreather(){
  let el=document.getElementById('waveBreather');
  el.style.display='block';
  let c=document.getElementById('breatherCount');
  c.textContent=Math.ceil(breatherTimer);
}

function updateBreather(dt){
  if(!waveBreather) return;
  breatherTimer-=dt;
  document.getElementById('breatherCount').textContent=Math.ceil(Math.max(0,breatherTimer));
  if(breatherTimer<=0){
    waveBreather=false;
    document.getElementById('waveBreather').style.display='none';
    startNextWave();
  }
}

function updateParticles(dt){
  for(let i=particles.length-1;i>=0;i--){
    let p=particles[i];
    p.x+=p.vx*60*dt;p.y+=p.vy*60*dt;
    p.life-=dt;p.vy+=200*dt;
    if(p.life<=0) particles.splice(i,1);
  }
}

function spawnParticles(x,y,n,color,speed){
  for(let i=0;i<n;i++){
    let a=Math.random()*Math.PI*2;
    let s=(speed||5)*(0.5+Math.random()*0.5);
    particles.push({x,y,vx:Math.cos(a)*s,vy:Math.sin(a)*s-2,life:0.4+Math.random()*0.4,color:color||'#fff',r:2+Math.random()*2});
  }
}

function spawnFloat(x,y,text,color){
  floatNums.push({x,y:y,text,color:color||'#fff',life:1.2,vy:-40});
}

function updateFloatNums(){
  let now=Date.now();
  // Managed via DOM elements - just track array
  floatNums=floatNums.filter(f=>{f.life-=deltaTime;f.y+=f.vy*deltaTime;return f.life>0;});
}

function updateEffect(dt){
  if(!activeEffect) return;
  effectTimer-=dt;
  if(hasEffect('shield')&&!localPlayer.shield) localPlayer.shield=true;
  if(effectTimer<=0){
    if(activeEffect.id==='shield') localPlayer.shield=false;
    activeEffect=null;effectTimer=0;
    renderEffectDisplay();
  } else {
    renderEffectDisplay();
  }
}

function hasEffect(id){
  return activeEffect&&activeEffect.id===id;
}

function updateRespawn(dt){
  if(!respawning) return;
  respawnTimer-=dt;
  document.getElementById('respawnCount').textContent=Math.ceil(Math.max(0,respawnTimer));
  if(respawnTimer<=0){
    respawning=false;
    localPlayer.dead=false;
    localPlayer.hp=50;
    localPlayer.x=SAFE_X+(Math.random()*60-30);
    localPlayer.y=SAFE_Y+100;
    document.getElementById('respawnMsg').style.display='none';
  }
}

function startRespawn(){
  if(respawning) return;
  respawning=true;
  localPlayer.dead=true;
  localPlayer.hp=0;
  respawnTimer=5;
  document.getElementById('respawnMsg').style.display='block';
  document.getElementById('respawnCount').textContent='5';
}

function updateWaveNotif(){
  if(waveNotifTimer>0){waveNotifTimer-=deltaTime;}
  else{document.getElementById('waveNotif').style.opacity='0';}
}

function showWaveNotif(text){
  let el=document.getElementById('waveNotif');
  el.textContent=text;
  el.style.opacity='1';
  waveNotifTimer=2.5;
}

function updateHUD(){
  if(!localPlayer) return;
  document.getElementById('hudHp').textContent=Math.ceil(localPlayer.hp)+'/'+localPlayer.maxHp;
  document.getElementById('barHp').style.width=Math.max(0,localPlayer.hp/localPlayer.maxHp*100)+'%';
  document.getElementById('hudSafe').textContent=Math.ceil(safeHP)+'/'+safeMaxHP;
  document.getElementById('barSafe').style.width=Math.max(0,safeHP/safeMaxHP*100)+'%';
  document.getElementById('hudMoney').textContent='$'+Math.floor(localPlayer.money);
  document.getElementById('hudWave').textContent='Волна '+wave+(waveBreather?' (пауза)':waveActive?' [АКТИВНА]':'');
  let wk=localPlayer.weaponKey;
  let wi=localPlayer.weapons[wk];
  let ammoTxt=wi?(wi.maxAmmo===Infinity?'∞':wi.curAmmo+'/'+wi.maxAmmo+(wi.reloading?' [ПЕРЕЗ.]':'')):'';
  document.getElementById('hudWeapon').textContent=(WEAPONS[wk]?.name||'?')+' '+ammoTxt;

  let hpEl=document.getElementById('hudHp');
  hpEl.className='hud-val'+(localPlayer.hp<localPlayer.maxHp*0.3?' danger':'');
  let safeEl=document.getElementById('hudSafe');
  safeEl.className='hud-val'+(safeHP<safeMaxHP*0.3?' danger':'');
}

function updatePlayersList(){
  let el=document.getElementById('playersList');
  let html='';
  for(let id in players){
    let p=players[id];
    html+=`<div class="player-entry">
      <div class="player-dot" style="background:${p.color||'#f5c842'};"></div>
      <span style="color:${p.color||'#f5c842'}">${p.nick||'?'}</span>
      <span style="color:rgba(212,168,67,.6);margin-left:4px;">${Math.ceil(p.hp||0)}HP</span>
    </div>`;
  }
  el.innerHTML=html;
}

// ─── RENDER ───────────────────────────────────────────────────
function render(){
  ctx.clearRect(0,0,canvas.width,canvas.height);
  ctx.save();
  ctx.translate(-camX,-camY);
  drawWorld();
  drawDrops();
  drawTurrets();
  drawBullets();
  drawEnemies();
  drawPlayers();
  drawParticles();
  drawFloatNums();
  ctx.restore();
  drawMinimap();
}

function drawWorld(){
  // Background
  let bg=ctx.createPattern(drawFloorTile(),'repeat');
  ctx.fillStyle=bg||'#1a1200';
  ctx.fillRect(0,0,WORLD_W,WORLD_H);
  // Border
  ctx.strokeStyle='rgba(245,200,66,0.3)';
  ctx.lineWidth=4;
  ctx.strokeRect(2,2,WORLD_W-4,WORLD_H-4);
  // Obstacles
  drawObstacles();
  // Safe
  drawSafe();
  // Vending machines
  drawVendingMachine(VEND_X,VEND_Y,'food');
  drawVendingMachine(GAMB_X,GAMB_Y,'gambler');
}

let floorPattern=null;
let floorCanvasEl=null;
function drawFloorTile(){
  if(floorCanvasEl) return floorCanvasEl;
  let fc=document.createElement('canvas');fc.width=40;fc.height=40;
  let fx=fc.getContext('2d');
  fx.fillStyle='#1f1200';fx.fillRect(0,0,40,40);
  // Board lines
  fx.strokeStyle='rgba(100,60,10,0.35)';fx.lineWidth=1;
  fx.beginPath();fx.moveTo(0,0);fx.lineTo(40,40);fx.stroke();
  fx.beginPath();fx.moveTo(40,0);fx.lineTo(0,40);fx.stroke();
  // Plank lines
  fx.strokeStyle='rgba(60,35,0,0.55)';fx.lineWidth=1.5;
  fx.beginPath();fx.moveTo(0,20);fx.lineTo(40,20);fx.stroke();
  fx.beginPath();fx.moveTo(20,0);fx.lineTo(20,40);fx.stroke();
  // Grain dots
  fx.fillStyle='rgba(80,50,0,0.2)';
  [6,18,30].forEach(gx=>[8,24].forEach(gy=>{
    fx.beginPath();fx.arc(gx,gy,1,0,Math.PI*2);fx.fill();
  }));
  floorCanvasEl=fc;
  return fc;
}
function getFloorPattern(){
  if(floorPattern) return floorPattern;
  if(!ctx) return null;
  let tile=drawFloorTile();
  floorPattern=ctx.createPattern(tile,'repeat');
  return floorPattern;
}

function drawObstacles(){
  obstacles.forEach(o=>{
    if(o.type==='barrel'){
      // Barrel cluster
      ctx.save();
      ctx.translate(o.x+o.w/2,o.y+o.h/2);
      // Barrel body
      let grad=ctx.createRadialGradient(-4,-4,2,0,0,o.w/2);
      grad.addColorStop(0,'#8b5c1a');grad.addColorStop(1,'#3d2200');
      ctx.fillStyle=grad;
      ctx.beginPath();ctx.ellipse(0,0,o.w/2,o.h/2,0,0,Math.PI*2);ctx.fill();
      // Hoops
      ctx.strokeStyle='rgba(180,130,50,0.8)';ctx.lineWidth=2;
      [-8,0,8].forEach(yy=>{
        ctx.beginPath();ctx.ellipse(0,yy,o.w/2-1,3,0,0,Math.PI*2);ctx.stroke();
      });
      ctx.restore();
    } else if(o.type==='crate'){
      ctx.save();ctx.translate(o.x,o.y);
      ctx.fillStyle='#5c3a1e';ctx.fillRect(0,0,o.w,o.h);
      ctx.strokeStyle='rgba(180,130,50,0.6)';ctx.lineWidth=1.5;
      ctx.strokeRect(2,2,o.w-4,o.h-4);
      // Cross
      ctx.beginPath();ctx.moveTo(0,o.h/2);ctx.lineTo(o.w,o.h/2);ctx.stroke();
      ctx.beginPath();ctx.moveTo(o.w/2,0);ctx.lineTo(o.w/2,o.h);ctx.stroke();
      ctx.restore();
    } else if(o.type==='wagon'){
      ctx.save();ctx.translate(o.x,o.y);
      // Wagon body
      ctx.fillStyle='#6b3a2a';ctx.fillRect(0,8,o.w,o.h-16);
      ctx.fillStyle='#4a2518';ctx.fillRect(4,4,o.w-8,8);
      ctx.fillStyle='#4a2518';ctx.fillRect(4,o.h-12,o.w-8,8);
      // Wheels
      ctx.fillStyle='#2d1a00';
      [14,o.w-14].forEach(wx=>{
        ctx.beginPath();ctx.arc(wx,o.h-4,10,0,Math.PI*2);ctx.fill();
        ctx.strokeStyle='rgba(180,130,50,0.7)';ctx.lineWidth=2;
        ctx.beginPath();ctx.arc(wx,o.h-4,10,0,Math.PI*2);ctx.stroke();
        ctx.beginPath();ctx.moveTo(wx-8,o.h-4);ctx.lineTo(wx+8,o.h-4);ctx.stroke();
        ctx.beginPath();ctx.moveTo(wx,o.h-12);ctx.lineTo(wx,o.h+4);ctx.stroke();
      });
      ctx.restore();
    } else if(o.type==='wall'){
      ctx.save();ctx.translate(o.x,o.y);
      let g=ctx.createLinearGradient(0,0,o.w,0);
      g.addColorStop(0,'#3d2200');g.addColorStop(.5,'#5c3a1e');g.addColorStop(1,'#3d2200');
      ctx.fillStyle=g;ctx.fillRect(0,0,o.w,o.h);
      ctx.strokeStyle='rgba(180,130,50,0.5)';ctx.lineWidth=2;ctx.strokeRect(0,0,o.w,o.h);
      // Brick lines
      ctx.strokeStyle='rgba(30,15,0,0.5)';ctx.lineWidth=1;
      for(let by=0;by<o.h;by+=12){
        ctx.beginPath();ctx.moveTo(0,by);ctx.lineTo(o.w,by);ctx.stroke();
      }
      ctx.restore();
    } else if(o.type==='rock'){
      ctx.save();ctx.translate(o.x+o.w/2,o.y+o.h/2);
      let gr=ctx.createRadialGradient(-4,-4,2,0,0,Math.max(o.w,o.h)/2);
      gr.addColorStop(0,'#6b6b5a');gr.addColorStop(1,'#2d2d24');
      ctx.fillStyle=gr;
      ctx.beginPath();
      ctx.ellipse(0,0,o.w/2,o.h/2,0,0,Math.PI*2);ctx.fill();
      ctx.strokeStyle='rgba(140,130,100,0.4)';ctx.lineWidth=1;ctx.stroke();
      ctx.restore();
    }
  });
}

function drawSafe(){
  let x=SAFE_X-SAFE_W/2,y=SAFE_Y-SAFE_H/2;
  ctx.save();
  // Glow
  let pulse=0.7+Math.sin(Date.now()/600)*0.3;
  let glow=ctx.createRadialGradient(SAFE_X,SAFE_Y,10,SAFE_X,SAFE_Y,80);
  glow.addColorStop(0,`rgba(245,200,66,${0.15*pulse})`);
  glow.addColorStop(1,'rgba(245,200,66,0)');
  ctx.fillStyle=glow;ctx.fillRect(SAFE_X-80,SAFE_Y-80,160,160);

  // Safe body
  let bg=ctx.createLinearGradient(x,y,x+SAFE_W,y+SAFE_H);
  bg.addColorStop(0,'#4a4a4a');bg.addColorStop(.4,'#888');bg.addColorStop(1,'#2d2d2d');
  ctx.fillStyle=bg;ctx.beginPath();
  ctx.roundRect(x,y,SAFE_W,SAFE_H,4);ctx.fill();
  // Border
  ctx.strokeStyle=`rgba(245,200,66,${0.6+pulse*0.3})`;ctx.lineWidth=2.5;
  ctx.beginPath();ctx.roundRect(x,y,SAFE_W,SAFE_H,4);ctx.stroke();
  // Door line
  ctx.strokeStyle='rgba(200,200,200,0.5)';ctx.lineWidth=1.5;
  ctx.beginPath();ctx.moveTo(SAFE_X+6,y+6);ctx.lineTo(SAFE_X+6,y+SAFE_H-6);ctx.stroke();
  // Handle
  ctx.fillStyle='#f5c842';
  ctx.beginPath();ctx.arc(SAFE_X-6,SAFE_Y,8,0,Math.PI*2);ctx.fill();
  ctx.strokeStyle='#8b6914';ctx.lineWidth=2;
  ctx.beginPath();ctx.arc(SAFE_X-6,SAFE_Y,8,0,Math.PI*2);ctx.stroke();
  // Dial
  ctx.fillStyle='#666';ctx.beginPath();ctx.arc(SAFE_X-6,SAFE_Y,5,0,Math.PI*2);ctx.fill();
  let d=Date.now()/800;
  ctx.strokeStyle='#f5c842';ctx.lineWidth=1.5;
  ctx.beginPath();ctx.moveTo(SAFE_X-6,SAFE_Y);ctx.lineTo(SAFE_X-6+Math.cos(d)*4,SAFE_Y+Math.sin(d)*4);ctx.stroke();
  // Bolt holes
  ['#aaa','#aaa','#aaa','#aaa'].forEach((c,i)=>{
    let bx=x+8+(i%2)*56,by=y+8+Math.floor(i/2)*56;
    ctx.fillStyle=c;ctx.beginPath();ctx.arc(bx,by,4,0,Math.PI*2);ctx.fill();
  });
  // HP bar
  let bw=SAFE_W+20,bh=8,bx2=SAFE_X-bw/2,by2=y-18;
  ctx.fillStyle='rgba(0,0,0,0.7)';ctx.fillRect(bx2,by2,bw,bh);
  let pct=safeHP/safeMaxHP;
  let bc=pct>0.5?'#39ff14':pct>0.25?'#f5c842':'#ff4444';
  ctx.fillStyle=bc;ctx.fillRect(bx2,by2,bw*pct,bh);
  ctx.strokeStyle='rgba(245,200,66,0.4)';ctx.lineWidth=1;ctx.strokeRect(bx2,by2,bw,bh);
  // Label
  ctx.fillStyle='rgba(245,200,66,0.8)';ctx.font='bold 11px Oswald,sans-serif';
  ctx.textAlign='center';ctx.fillText('⬡ СЕЙФ',SAFE_X,by2-4);
  ctx.restore();
}

function drawVendingMachine(x,y,type){
  let isFood=type==='food';
  let w=44,h=70;
  ctx.save();
  ctx.translate(x-w/2,y-h/2);
  // Body
  let bg=ctx.createLinearGradient(0,0,w,h);
  bg.addColorStop(0,isFood?'#0a3020':'#200030');
  bg.addColorStop(1,isFood?'#051810':'#100018');
  ctx.fillStyle=bg;ctx.fillRect(0,0,w,h);
  // Glow border
  let pulse=0.6+Math.sin(Date.now()/700+x)*0.4;
  ctx.shadowBlur=12*pulse;
  ctx.shadowColor=isFood?'#39ff14':'#ff2d9b';
  ctx.strokeStyle=isFood?`rgba(57,255,20,${0.7+pulse*0.3})`:`rgba(255,45,155,${0.7+pulse*0.3})`;
  ctx.lineWidth=2;ctx.strokeRect(1,1,w-2,h-2);
  ctx.shadowBlur=0;
  // Screen
  ctx.fillStyle=isFood?'rgba(57,255,20,0.15)':'rgba(255,45,155,0.15)';
  ctx.fillRect(4,8,w-8,24);
  ctx.strokeStyle=isFood?'rgba(57,255,20,0.5)':'rgba(255,45,155,0.5)';
  ctx.lineWidth=1;ctx.strokeRect(4,8,w-8,24);
  // Screen text
  ctx.fillStyle=isFood?'#39ff14':'#ff2d9b';
  ctx.font='bold 7px Oswald,sans-serif';ctx.textAlign='center';
  ctx.fillText(isFood?'SHOP':'LUCK',w/2,22);
  ctx.font='6px Oswald,sans-serif';
  ctx.fillText(isFood?'[E]':'[E]',w/2,30);
  // Slots
  for(let i=0;i<3;i++){
    ctx.fillStyle='rgba(255,255,255,0.05)';
    ctx.fillRect(4+i*12,36,10,12);
    ctx.fillStyle=isFood?'rgba(57,255,20,0.3)':'rgba(255,45,155,0.3)';
    ctx.font='8px sans-serif';ctx.textAlign='center';
    ctx.fillText(['🍖','💊','🔫','🎰','🃏','⚡'][isFood?i:i+3],9+i*12,45);
  }
  // Coin slot
  ctx.fillStyle='#333';ctx.fillRect(w/2-8,54,16,4);ctx.strokeStyle='#555';ctx.lineWidth=1;ctx.strokeRect(w/2-8,54,16,4);
  // Label
  ctx.fillStyle=isFood?'rgba(57,255,20,0.7)':'rgba(255,45,155,0.7)';
  ctx.font='bold 7px Oswald,sans-serif';ctx.textAlign='center';
  ctx.fillText(isFood?'SALOON':'FORTUNE',w/2,64);
  ctx.restore();
  // Interact hint
  let dx=localPlayer?localPlayer.x-(x):999;
  let dy=localPlayer?localPlayer.y-(y):999;
  if(localPlayer&&Math.sqrt(dx*dx+dy*dy)<INTERACT_DIST){
    ctx.fillStyle=isFood?'rgba(57,255,20,0.9)':'rgba(255,45,155,0.9)';
    ctx.font='bold 12px Oswald,sans-serif';ctx.textAlign='center';
    ctx.fillText('[E] Взаимодействие',x,y-h/2-10);
  }
}

function drawPlayers(){
  for(let id in players){
    let p=players[id];
    if(id!==myId&&p.tx!==undefined){
      // Interpolate remote players
      p.x=p.x||p.tx; p.y=p.y||p.ty;
      p.x+=(p.tx-p.x)*0.2;
      p.y+=(p.ty-p.y)*0.2;
    }
    if(p.dead) continue;
    drawPlayer(p,id===myId);
  }
}

function drawPlayer(p,isLocal){
  ctx.save();
  ctx.translate(p.x,p.y);
  // Shadow
  ctx.fillStyle='rgba(0,0,0,0.3)';ctx.beginPath();ctx.ellipse(0,8,PLAYER_R,6,0,0,Math.PI*2);ctx.fill();
  // Shield glow
  if(p.shield||hasEffect('shield')&&isLocal){
    ctx.beginPath();ctx.arc(0,0,PLAYER_R+5,0,Math.PI*2);
    ctx.strokeStyle='rgba(52,152,219,0.7)';ctx.lineWidth=3;ctx.stroke();
  }
  // Body
  let c=p.color||'#f5c842';
  ctx.rotate(p.angle||0);
  // Hat
  ctx.fillStyle='#2d1a00';
  ctx.beginPath();ctx.ellipse(0,-PLAYER_R+2,PLAYER_R-2,5,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#3d2700';
  ctx.fillRect(-PLAYER_R-3,-PLAYER_R+5,PLAYER_R*2+6,5);
  ctx.fillStyle='#2d1a00';
  ctx.fillRect(-6,-PLAYER_R-8,12,18);
  // Body circle
  ctx.rotate(-p.angle||0);
  let bodyG=ctx.createRadialGradient(-3,-3,1,0,0,PLAYER_R);
  bodyG.addColorStop(0,lightenColor(c,40));bodyG.addColorStop(1,c);
  ctx.fillStyle=bodyG;
  ctx.beginPath();ctx.arc(0,0,PLAYER_R,0,Math.PI*2);ctx.fill();
  ctx.strokeStyle='rgba(0,0,0,0.4)';ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(0,0,PLAYER_R,0,Math.PI*2);ctx.stroke();
  // Arms / weapon
  ctx.rotate(p.angle||0);
  let wk=p.weaponKey||'pistol';
  let wDef=WEAPONS[wk];
  // Gun
  ctx.fillStyle=wDef?.color||'#888';
  ctx.fillRect(PLAYER_R-2,-3,18,6);
  ctx.fillStyle='#555';ctx.fillRect(PLAYER_R+10,-2,6,4);
  // Muzzle flash
  if(isLocal&&Date.now()-localPlayer.lastFire<80){
    ctx.fillStyle='rgba(255,220,50,0.9)';
    ctx.beginPath();ctx.arc(PLAYER_R+16,0,5,0,Math.PI*2);ctx.fill();
  }
  ctx.restore();
  // Nick above
  ctx.save();ctx.translate(p.x,p.y);
  ctx.fillStyle=p.color||'#f5c842';
  ctx.font='bold 11px Oswald,sans-serif';ctx.textAlign='center';
  ctx.shadowColor='rgba(0,0,0,0.8)';ctx.shadowBlur=4;
  ctx.fillText(p.nick||'?',0,-PLAYER_R-14);
  ctx.restore();
  // HP bar
  if(!isLocal){
    let bw=PLAYER_R*2+10,bh=4,bx=p.x-bw/2,by=p.y-PLAYER_R-10;
    ctx.fillStyle='rgba(0,0,0,0.6)';ctx.fillRect(bx,by,bw,bh);
    ctx.fillStyle='#39ff14';ctx.fillRect(bx,by,bw*(p.hp/p.maxHp||0),bh);
  }
}

function lightenColor(hex,amt){
  let r=parseInt(hex.slice(1,3),16),g=parseInt(hex.slice(3,5),16),b=parseInt(hex.slice(5,7),16);
  return `rgb(${Math.min(255,r+amt)},${Math.min(255,g+amt)},${Math.min(255,b+amt)})`;
}

function drawBullets(){
  bullets.forEach(b=>{
    ctx.save();
    let alpha=Math.min(1,b.life*2);
    if(b.owner==='player'){
      ctx.shadowBlur=8;ctx.shadowColor=b.color||'#f5c842';
    }
    ctx.fillStyle=b.color||(b.owner==='player'?'#f5c842':'#ff4444');
    ctx.globalAlpha=alpha;
    ctx.beginPath();ctx.arc(b.x,b.y,b.r||2.5,0,Math.PI*2);ctx.fill();
    // Trail
    ctx.globalAlpha=alpha*0.4;
    ctx.fillStyle=b.color||'#fff';
    ctx.beginPath();ctx.arc(b.x-b.vx*2,b.y-b.vy*2,b.r*0.7||1.5,0,Math.PI*2);ctx.fill();
    ctx.restore();
  });
}

function drawEnemies(){
  enemies.forEach(e=>{
    if(e.dead) return;
    drawEnemy(e);
  });
}

function drawEnemy(e){
  ctx.save();ctx.translate(e.x,e.y);
  // Shadow
  ctx.fillStyle='rgba(0,0,0,0.3)';ctx.beginPath();ctx.ellipse(0,e.radius*0.6,e.radius*0.8,e.radius*0.3,0,0,Math.PI*2);ctx.fill();
  // Shield
  if(e.shield){
    ctx.strokeStyle='rgba(52,152,219,0.8)';ctx.lineWidth=3;
    ctx.beginPath();ctx.arc(0,0,e.radius+6,0,Math.PI*2);ctx.stroke();
  }
  // Body
  let grad=ctx.createRadialGradient(-e.radius*0.3,-e.radius*0.3,1,0,0,e.radius);
  grad.addColorStop(0,lightenColor(e.color,30));grad.addColorStop(1,e.color);
  ctx.fillStyle=grad;
  if(e.isBoss){
    // Boss: star shape
    ctx.beginPath();
    for(let i=0;i<8;i++){
      let a=Math.PI*i/4;
      let r=i%2===0?e.radius:e.radius*0.6;
      i===0?ctx.moveTo(Math.cos(a)*r,Math.sin(a)*r):ctx.lineTo(Math.cos(a)*r,Math.sin(a)*r);
    }
    ctx.closePath();ctx.fill();
  } else {
    ctx.beginPath();ctx.arc(0,0,e.radius,0,Math.PI*2);ctx.fill();
  }
  ctx.strokeStyle='rgba(0,0,0,0.5)';ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(0,0,e.radius,0,Math.PI*2);ctx.stroke();

  // Type icon
  let icon={'grunt':'🤠','runner':'💨','heavy':'🔨','shooter':'🔫','bomber':'💣','boss':'☠️'}[e.type]||'👤';
  ctx.font=`${e.radius}px sans-serif`;ctx.textAlign='center';
  ctx.fillText(icon,0,e.radius*0.4);
  ctx.restore();

  // HP bar
  let bw=e.radius*2+10,bh=5,bx=e.x-bw/2,by=e.y-e.radius-10;
  ctx.fillStyle='rgba(0,0,0,0.7)';ctx.fillRect(bx,by,bw,bh);
  let pct=e.hp/e.maxHp;
  ctx.fillStyle=pct>0.5?'#2ecc71':pct>0.25?'#f39c12':'#e74c3c';
  ctx.fillRect(bx,by,bw*pct,bh);
  ctx.strokeStyle='rgba(255,255,255,0.2)';ctx.lineWidth=0.5;ctx.strokeRect(bx,by,bw,bh);

  // Boss label
  if(e.isBoss){
    ctx.fillStyle='#ff2200';ctx.font='bold 12px Oswald,sans-serif';ctx.textAlign='center';
    ctx.shadowColor='rgba(255,34,0,0.8)';ctx.shadowBlur=8;
    ctx.fillText('★ БОСС ★',e.x,by-5);ctx.shadowBlur=0;
  }
  // Slow aura
  if(e.slowAura){
    ctx.save();ctx.translate(e.x,e.y);
    let t=Date.now()/1000;
    let alpha=0.15+Math.sin(t*3)*0.1;
    ctx.strokeStyle=`rgba(138,43,226,${alpha})`;ctx.lineWidth=2;
    ctx.beginPath();ctx.arc(0,0,120,0,Math.PI*2);ctx.stroke();
    ctx.restore();
  }
}

function drawDrops(){
  drops.forEach(d=>{
    let pulse=0.7+Math.sin(Date.now()/300)*0.3;
    ctx.save();ctx.translate(d.x,d.y);
    ctx.globalAlpha=Math.min(1,d.life)*pulse;
    let icon={'hp':'❤️','money':'💰','ammo':'🔫'}[d.type]||'?';
    ctx.font='18px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText(icon,0,0);
    ctx.restore();
  });
}

function drawTurrets(){
  turrets.forEach(t=>{
    ctx.save();ctx.translate(t.x,t.y);
    // Base
    ctx.fillStyle='#4a3000';ctx.beginPath();ctx.arc(0,0,14,0,Math.PI*2);ctx.fill();
    ctx.strokeStyle='rgba(57,255,20,0.6)';ctx.lineWidth=2;ctx.beginPath();ctx.arc(0,0,14,0,Math.PI*2);ctx.stroke();
    // Find nearest enemy for direction
    let angle=0;
    let nearE=enemies.reduce((b,e)=>{
      if(e.dead) return b;
      let d=(e.x-t.x)**2+(e.y-t.y)**2;
      return(!b||d<b.d)?{e,d}:b;
    },null);
    if(nearE&&nearE.d<TURRET_RANGE*TURRET_RANGE) angle=Math.atan2(nearE.e.y-t.y,nearE.e.x-t.x);
    ctx.rotate(angle);
    ctx.fillStyle='#39ff14';ctx.fillRect(0,-3,18,6);
    ctx.restore();
    // HP bar
    let bw=28,bh=4,bx=t.x-bw/2,by=t.y-20;
    ctx.fillStyle='rgba(0,0,0,0.6)';ctx.fillRect(bx,by,bw,bh);
    ctx.fillStyle='#39ff14';ctx.fillRect(bx,by,bw*(t.hp/t.maxHp||1),bh);
  });
}

function drawParticles(){
  particles.forEach(p=>{
    ctx.save();
    ctx.globalAlpha=p.life;
    ctx.fillStyle=p.color;
    ctx.beginPath();ctx.arc(p.x,p.y,p.r||2,0,Math.PI*2);ctx.fill();
    ctx.restore();
  });
}

function drawFloatNums(){
  floatNums.forEach(f=>{
    ctx.save();
    ctx.globalAlpha=f.life;
    ctx.fillStyle=f.color||'#fff';
    ctx.font='bold 14px Oswald,sans-serif';
    ctx.textAlign='center';
    ctx.shadowColor='rgba(0,0,0,0.8)';ctx.shadowBlur=4;
    ctx.fillText(f.text,f.x,f.y);
    ctx.restore();
  });
}

function drawMinimap(){
  let mc=document.getElementById('minimap');
  let mx=mc.width,my=mc.height;
  miniCtx.clearRect(0,0,mx,my);
  miniCtx.fillStyle='rgba(10,5,0,0.85)';miniCtx.fillRect(0,0,mx,my);
  let sx=mx/WORLD_W,sy=my/WORLD_H;
  // Obstacles
  miniCtx.fillStyle='rgba(92,58,30,0.6)';
  obstacles.forEach(o=>{miniCtx.fillRect(o.x*sx,o.y*sy,o.w*sx,o.h*sy);});
  // Safe
  miniCtx.fillStyle='rgba(245,200,66,0.8)';
  miniCtx.fillRect((SAFE_X-SAFE_W/2)*sx,(SAFE_Y-SAFE_H/2)*sy,SAFE_W*sx,SAFE_H*sy);
  // Enemies
  miniCtx.fillStyle='#ff4444';
  enemies.forEach(e=>{if(!e.dead)miniCtx.fillRect(e.x*sx-1.5,e.y*sy-1.5,3,3);});
  // Players
  for(let id in players){
    let p=players[id];
    if(p.dead) continue;
    miniCtx.fillStyle=p.color||'#f5c842';
    miniCtx.beginPath();miniCtx.arc(p.x*sx,p.y*sy,3,0,Math.PI*2);miniCtx.fill();
  }
}

// ─── GAME OVER ────────────────────────────────────────────────
function triggerGameOver(){
  if(gameOver) return;
  gameOver=true;
  waveActive=false;
  showGameOver(false);
}

function showGameOver(disconnected){
  document.getElementById('gameOver').style.display='flex';
  let stats=`<div>Выживших волн: <span class="stat-val">${wave}</span></div>
  <div>Уничтожено врагов: <span class="stat-val">${totalKills}</span></div>
  <div>Накопленные деньги: <span class="stat-val">$${Math.floor(localPlayer?.money||0)}</span></div>`;
  if(disconnected) stats='<div style="color:#ff6b6b;">Связь с сервером потеряна.</div>'+stats;
  document.getElementById('goStats').innerHTML=stats;
  // Save to leaderboard
  if(gameMode==='solo'){
    let lb=JSON.parse(localStorage.getItem('vs_lb')||'[]');
    lb.push({nick:nickname,wave,kills:totalKills,date:new Date().toLocaleDateString()});
    lb.sort((a,b)=>b.wave-a.wave||b.kills-a.kills);
    lb=lb.slice(0,10);
    localStorage.setItem('vs_lb',JSON.stringify(lb));
  }
  showLeaderboard();
}

function restartGame(){
  // Reset all
  enemies=[];bullets=[];particles=[];floatNums=[];drops=[];turrets=[];
  safeHP=1000;safeMaxHP=1000;safeLevel=1;
  wave=0;waveActive=false;waveBreather=false;
  totalKills=0;gameOver=false;
  activeEffect=null;effectTimer=0;
  respawning=false;
  if(localPlayer){
    localPlayer.x=SAFE_X;localPlayer.y=SAFE_Y+120;
    localPlayer.hp=100;localPlayer.money=0;localPlayer.dead=false;
    localPlayer.weaponKey='pistol';
    localPlayer.weapons={pistol:{...WEAPONS.pistol,curAmmo:Infinity,reloading:false}};
    localPlayer.kills=0;
  }
  document.getElementById('gameOver').style.display='none';
  if(gameMode==='solo') startNextWave();
}

function goToMenu(){
  if(socket){socket.disconnect();socket=null;}
  document.getElementById('gameOver').style.display='none';
  document.getElementById('gameContainer').style.display='none';
  document.getElementById('mainMenu').style.display='flex';
  document.getElementById('mainMenu').style.opacity='1';
  cancelAnimationFrame(animId);
  gameMode=null;players={};localPlayer=null;
  initMenuParticles();
}

// ─── HELPERS ──────────────────────────────────────────────────
function addChat(msg){
  let el=document.getElementById('chatMessages');
  let div=document.createElement('div');
  div.className='chat-line';div.textContent=msg;
  el.prepend(div);
  while(el.children.length>5) el.removeChild(el.lastChild);
}

function createRemotePlayer(id,data){
  return {
    id,nick:data.nick||'Player',
    x:data.x||SAFE_X,y:data.y||SAFE_Y+100,
    tx:data.x||SAFE_X,ty:data.y||SAFE_Y+100,
    angle:data.angle||0,
    hp:data.hp||100,maxHp:100,
    money:data.money||0,
    color:PLAYER_COLORS[Object.keys(players).length%PLAYER_COLORS.length],
    weaponKey:data.weapon||'pistol',
    dead:false,shield:false,
  };
}

// ─── WINDOW RESIZE ────────────────────────────────────────────
window.addEventListener('resize',()=>{
  if(menuCanvas){menuCanvas.width=window.innerWidth;menuCanvas.height=window.innerHeight;}
  if(canvas){canvas.width=window.innerWidth;canvas.height=window.innerHeight;}
});

// ─── LEADERBOARD IN GAME OVER ─────────────────────────────────
function showLeaderboard(){
  let lb=JSON.parse(localStorage.getItem('vs_lb')||'[]');
  if(lb.length===0) return;
  let html='<div style="margin-top:14px;border-top:1px solid rgba(245,200,66,.3);padding-top:10px;">';
  html+='<div style="font-family:Oswald,sans-serif;font-size:12px;letter-spacing:2px;color:var(--sand);margin-bottom:6px;">🏆 ТАБЛИЦА РЕКОРДОВ</div>';
  lb.forEach((e,i)=>{
    html+=`<div style="font-family:Oswald,sans-serif;font-size:12px;color:${i===0?'#f5c842':'rgba(212,168,67,.7)'};display:flex;justify-content:space-between;gap:20px;">
      <span>${i+1}. ${e.nick}</span><span>Волна ${e.wave}</span><span>${e.kills} кил.</span><span style="opacity:.5;">${e.date}</span></div>`;
  });
  html+='</div>';
  document.getElementById('goStats').insertAdjacentHTML('beforeend',html);
}

// ─── ROUNDRECT POLYFILL ────────────────────────────────────────
if(!CanvasRenderingContext2D.prototype.roundRect){
  CanvasRenderingContext2D.prototype.roundRect=function(x,y,w,h,r){
    r=Math.min(r,w/2,h/2);
    this.beginPath();
    this.moveTo(x+r,y);
    this.lineTo(x+w-r,y);this.arcTo(x+w,y,x+w,y+r,r);
    this.lineTo(x+w,y+h-r);this.arcTo(x+w,y+h,x+w-r,y+h,r);
    this.lineTo(x+r,y+h);this.arcTo(x,y+h,x,y+h-r,r);
    this.lineTo(x,y+r);this.arcTo(x,y,x+r,y,r);
    this.closePath();
    return this;
  };
}

// ─── INIT ─────────────────────────────────────────────────────
initMenuParticles();
</script>
</body>
</html>

"""

os.makedirs('templates', exist_ok=True)
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html_code)
print('✅ HTML сохранён в templates/index.html')

# 2. Серверная часть (полная, все функции на месте)

import os
import sys
import time
import math
import random
import threading
from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO, emit, disconnect
from flask_cors import CORS

# ─── КОНФИГУРАЦИЯ ──────────────────────────────────────────────────
SECRET_KEY = os.urandom(24).hex()
MAX_PLAYERS = 6
TICK_RATE = 20
TICK_INTERVAL = 1.0 / TICK_RATE
WORLD_W, WORLD_H = 1200, 840
SAFE_X, SAFE_Y = WORLD_W // 2, WORLD_H // 2
SAFE_W, SAFE_H = 72, 80
PLAYER_R = 14
BREATHER_DURATION = 12

# ─── FLASK ПРИЛОЖЕНИЕ ────────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
CORS(app, origins="*")
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',   # ← Многопоточный режим
    logger=False,
    engineio_logger=False,
    ping_timeout=20,
    ping_interval=10
)

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

# ─── ГЛОБАЛЬНОЕ СОСТОЯНИЕ ─────────────────────────────────────────
game_lock = threading.Lock()

game_state = {
    'players': {},
    'enemies': [],
    'turrets': [],
    'safe_hp': 1000,
    'safe_max_hp': 1000,
    'safe_level': 1,
    'wave': 0,
    'wave_active': False,
    'wave_breather': False,
    'wave_enemy_count': 0,
    'wave_killed': 0,
    'game_over': False,
    'enemy_id_counter': 0,
    'last_tick': time.time(),
    'breather_timer': 0,
}

WEAPONS = {
    'pistol':  {'damage': 22, 'bullet_speed': 9},
    'shotgun': {'damage': 30, 'pellets': 6, 'bullet_speed': 8},
    'rifle':   {'damage': 14, 'bullet_speed': 10},
    'sniper':  {'damage': 90, 'bullet_speed': 16},
}

EFFECTS = [
    'dmg_up', 'spd_up', 'inf_ammo', 'regen', 'shield',
    'slow', 'invert', 'dmg_down', 'money_drain', 'drunk'
]

# ─── ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ──────────────────────────────────────
def dist(ax, ay, bx, by):
    return math.sqrt((ax - bx)**2 + (ay - by)**2)

def get_enemy_stats(etype, wave, is_boss=False):
    wm = 1 + wave * 0.12
    if is_boss or etype == 'boss':
        abilities_pool = ['minions', 'shield', 'regen', 'slow_aura', 'teleport', 'ranged_attack']
        num_abilities = min(4, 2 + wave // 5)
        abilities = random.sample(abilities_pool, num_abilities)
        return {
            'hp': int(800 * wm), 'max_hp': int(800 * wm),
            'speed': round(1.0 * wm, 2), 'damage': round(35 * wm, 1),
            'reward': 200, 'radius': 28, 'color': '#ff2200',
            'attack_range': 50, 'attack_rate': 1.8,
            'shoot_range': 280, 'shoot_rate': 2.0,
            'abilities': abilities, 'ability_timer': 0,
            'type': 'boss', 'is_boss': True,
            'shield': False, 'shield_hp': 0, 'slow_aura': False,
        }
    stats = {
        'grunt':   {'hp': int(60*wm), 'max_hp': int(60*wm), 'speed': round(1.4*wm,2), 'damage': round(12*wm,1), 'reward': 20, 'radius': 13, 'color': '#c0392b', 'attack_range': 30, 'attack_rate': 1.0, 'shoot_range': 0, 'shoot_rate': 99},
        'runner':  {'hp': int(30*wm), 'max_hp': int(30*wm), 'speed': round(2.8*wm,2), 'damage': round(8*wm,1),  'reward': 12, 'radius': 11, 'color': '#e67e22', 'attack_range': 25, 'attack_rate': 0.8, 'shoot_range': 0, 'shoot_rate': 99},
        'heavy':   {'hp': int(180*wm),'max_hp': int(180*wm),'speed': round(0.8*wm,2), 'damage': round(30*wm,1), 'reward': 40, 'radius': 20, 'color': '#8e44ad', 'attack_range': 35, 'attack_rate': 2.0, 'shoot_range': 0, 'shoot_rate': 99},
        'shooter': {'hp': int(50*wm), 'max_hp': int(50*wm), 'speed': round(1.2*wm,2), 'damage': round(10*wm,1), 'reward': 25, 'radius': 12, 'color': '#3498db', 'attack_range': 30, 'attack_rate': 1.5, 'shoot_range': 260, 'shoot_rate': 1.2},
        'bomber':  {'hp': int(40*wm), 'max_hp': int(40*wm), 'speed': round(1.8*wm,2), 'damage': round(50*wm,1), 'reward': 30, 'radius': 14, 'color': '#f39c12', 'attack_range': 40, 'attack_rate': 99, 'shoot_range': 0, 'shoot_rate': 99},
    }.get(etype, {
        'hp': int(60*wm), 'max_hp': int(60*wm), 'speed': round(1.4*wm,2), 'damage': round(12*wm,1),
        'reward': 20, 'radius': 13, 'color': '#c0392b', 'attack_range': 30, 'attack_rate': 1.0, 'shoot_range': 0, 'shoot_rate': 99,
    })
    stats.update({'abilities': [], 'ability_timer': 0, 'is_boss': False, 'shield': False, 'shield_hp': 0, 'slow_aura': False})
    return stats

def get_spawn_pos():
    side = random.randint(0, 3)
    margin = 25
    if side == 0:   return {'x': random.uniform(0, WORLD_W), 'y': margin}
    elif side == 1: return {'x': WORLD_W - margin, 'y': random.uniform(0, WORLD_H)}
    elif side == 2: return {'x': random.uniform(0, WORLD_W), 'y': WORLD_H - margin}
    else:           return {'x': margin, 'y': random.uniform(0, WORLD_H)}

def choose_enemy_type(wave):
    pool = ['grunt']
    if wave >= 2: pool.append('runner')
    if wave >= 3: pool.append('heavy')
    if wave >= 4: pool.append('shooter')
    if wave >= 5: pool.append('bomber')
    return random.choice(pool)

def new_enemy(etype, wave, is_boss=False):
    pos = get_spawn_pos()
    gs = game_state
    gs['enemy_id_counter'] += 1
    stats = get_enemy_stats(etype, wave, is_boss)
    return {
        'id': f'e{gs["enemy_id_counter"]}',
        'x': pos['x'], 'y': pos['y'],
        'type': etype,
        'dead': False,
        'last_attack': 0,
        'last_shot': 0,
        'last_ability': 0,
        **stats,
    }

def get_serializable_state():
    gs = game_state
    return {
        'players': {
            sid: {
                'x': p['x'], 'y': p['y'], 'angle': p.get('angle', 0),
                'hp': p['hp'], 'money': p['money'],
                'nick': p['nick'], 'weapon': p.get('weapon', 'pistol'),
                'dead': p.get('dead', False),
            }
            for sid, p in gs['players'].items()
        },
        'enemies': [
            {
                'id': e['id'], 'x': e['x'], 'y': e['y'],
                'hp': e['hp'], 'max_hp': e['max_hp'],
                'type': e['type'], 'is_boss': e.get('is_boss', False),
                'radius': e['radius'], 'color': e['color'],
                'shield': e.get('shield', False),
                'slow_aura': e.get('slow_aura', False),
            }
            for e in gs['enemies'] if not e.get('dead', False)
        ],
        'turrets': [
            {'id': t['id'], 'x': t['x'], 'y': t['y'], 'hp': t['hp'], 'max_hp': t['max_hp']}
            for t in gs['turrets']
        ],
        'safeHP': gs['safe_hp'],
        'safeMaxHP': gs['safe_max_hp'],
        'safeLevel': gs['safe_level'],
        'wave': gs['wave'],
        'waveActive': gs['wave_active'],
        'waveBreather': gs['wave_breather'],
        'gameOver': gs['game_over'],
    }

# ─── ОБРАБОТЧИКИ SOCKET.IO ────────────────────────────────────────
@socketio.on('connect')
def on_connect():
    sid = request.sid
    with game_lock:
        if len(game_state['players']) >= MAX_PLAYERS:
            disconnect()
            return

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    with game_lock:
        if sid in game_state['players']:
            del game_state['players'][sid]
    socketio.emit('state_update', get_serializable_state())

@socketio.on('join')
def on_join(data):
    sid = request.sid
    nick = str(data.get('nick', 'Cowboy'))[:16]
    with game_lock:
        gs = game_state
        spawn_x = SAFE_X + random.randint(-80, 80)
        spawn_y = SAFE_Y + 120
        gs['players'][sid] = {
            'id': sid, 'nick': nick,
            'x': spawn_x, 'y': spawn_y,
            'angle': 0,
            'hp': 100, 'max_hp': 100,
            'money': 50,
            'weapon': 'pistol',
            'dead': False,
            'last_damage': 0,
        }
        init_data = {
            'id': sid,
            'safeHP': gs['safe_hp'],
            'safeMaxHP': gs['safe_max_hp'],
            'safeLevel': gs['safe_level'],
            'wave': gs['wave'],
            'waveActive': gs['wave_active'],
            'players': {
                s: {'x': p['x'], 'y': p['y'], 'nick': p['nick'],
                    'hp': p['hp'], 'money': p['money'], 'weapon': p.get('weapon','pistol')}
                for s, p in gs['players'].items()
            },
        }
    emit('init', init_data)
    with game_lock:
        if not gs['wave_active'] and not gs['wave_breather'] and gs['wave'] == 0:
            start_next_wave()

@socketio.on('move')
def on_move(data):
    sid = request.sid
    with game_lock:
        if sid not in game_state['players']:
            return
        p = game_state['players'][sid]
        if p.get('dead', False):
            return
        nx = max(PLAYER_R, min(WORLD_W - PLAYER_R, float(data.get('x', p['x']))))
        ny = max(PLAYER_R, min(WORLD_H - PLAYER_R, float(data.get('y', p['y']))))
        dx, dy = nx - p['x'], ny - p['y']
        dist_moved = math.sqrt(dx*dx + dy*dy)
        if dist_moved > 8.0:
            scale = 8.0 / dist_moved
            nx = p['x'] + dx * scale
            ny = p['y'] + dy * scale
        p['x'] = nx
        p['y'] = ny
        p['angle'] = float(data.get('angle', 0))
        p['weapon'] = str(data.get('weapon', p.get('weapon', 'pistol')))

@socketio.on('shoot')
def on_shoot(data):
    sid = request.sid
    with game_lock:
        if sid not in game_state['players']:
            return
        p = game_state['players'][sid]
        if p.get('dead', False):
            return
        weapon_key = data.get('weaponKey', 'pistol')
        weapon = WEAPONS.get(weapon_key, WEAPONS['pistol'])
        bx = float(data.get('x', p['x']))
        by = float(data.get('y', p['y']))
        bvx = float(data.get('vx', 0))
        bvy = float(data.get('vy', 0))
        dmg = int(data.get('damage', weapon['damage']))
        dmg = max(1, min(dmg, weapon['damage'] * 2))
        check_bullet_hits(sid, bx, by, bvx, bvy, dmg)

def check_bullet_hits(shooter_sid, bx, by, bvx, bvy, dmg):
    speed = math.sqrt(bvx*bvx + bvy*bvy)
    if speed == 0:
        return
    nx, ny = bvx / speed, bvy / speed
    steps = 50
    step_size = 18.0
    cx, cy = bx, by
    for _ in range(steps):
        cx += nx * step_size
        cy += ny * step_size
        if cx < 0 or cx > WORLD_W or cy < 0 or cy > WORLD_H:
            break
        for e in game_state['enemies']:
            if e.get('dead', False):
                continue
            if dist(cx, cy, e['x'], e['y']) < e['radius'] + 6:
                apply_enemy_damage(e, dmg, shooter_sid)
                return

def apply_enemy_damage(enemy, dmg, shooter_sid):
    gs = game_state
    if enemy.get('shield', False):
        enemy['shield_hp'] -= dmg
        if enemy['shield_hp'] <= 0:
            enemy['shield'] = False
        socketio.emit('enemy_hit', {'id': enemy['id'], 'x': enemy['x'], 'y': enemy['y'], 'dmg': dmg, 'killed': False})
        return
    enemy['hp'] -= dmg
    killed = enemy['hp'] <= 0
    if killed:
        enemy['dead'] = True
        enemy['hp'] = 0
        gs['wave_killed'] += 1
        reward = enemy.get('reward', 20)
        if shooter_sid and shooter_sid in gs['players']:
            gs['players'][shooter_sid]['money'] += reward
        socketio.emit('enemy_hit', {'id': enemy['id'], 'x': enemy['x'], 'y': enemy['y'], 'dmg': dmg, 'killed': True, 'moneyReward': reward})
        if enemy['type'] == 'bomber':
            handle_bomber_explosion(enemy)
    else:
        socketio.emit('enemy_hit', {'id': enemy['id'], 'x': enemy['x'], 'y': enemy['y'], 'dmg': dmg, 'killed': False})

def handle_bomber_explosion(bomber):
    gs = game_state
    ex, ey = bomber['x'], bomber['y']
    radius = 80
    dmg = bomber['damage'] * 0.5
    for e in gs['enemies']:
        if e.get('dead') or e is bomber:
            continue
        if dist(ex, ey, e['x'], e['y']) < radius:
            apply_enemy_damage(e, int(dmg), None)
    if dist(ex, ey, SAFE_X, SAFE_Y) < 140:
        gs['safe_hp'] = max(0, gs['safe_hp'] - int(dmg * 0.5))
        socketio.emit('safe_hit', {'hp': gs['safe_hp'], 'dmg': int(dmg * 0.5)})
        if gs['safe_hp'] <= 0:
            trigger_game_over()
    for sid, p in gs['players'].items():
        if p.get('dead'):
            continue
        if dist(ex, ey, p['x'], p['y']) < radius:
            hit_dmg = int(dmg * 0.7)
            p['hp'] -= hit_dmg
            socketio.emit('player_hit', {'id': sid, 'hp': p['hp'], 'dmg': hit_dmg})
            if p['hp'] <= 0:
                kill_player(sid)

@socketio.on('buy')
def on_buy(data):
    sid = request.sid
    with game_lock:
        if sid not in game_state['players']:
            return
        p = game_state['players'][sid]
        gs = game_state
        btype = data.get('type', '')
        cost = int(data.get('cost', 0))
        if p['money'] < cost:
            emit('buy_result', {'ok': False, 'reason': 'Недостаточно денег'})
            return
        p['money'] -= cost
        result = {'ok': True, 'money': p['money']}
        if btype == 'repair_safe':
            gs['safe_hp'] = gs['safe_max_hp']
        elif btype == 'upgrade_safe':
            gs['safe_level'] += 1
            gs['safe_max_hp'] += 200
            gs['safe_hp'] = min(gs['safe_hp'] + 200, gs['safe_max_hp'])
        elif btype == 'heal':
            amount = int(data.get('amount', 50))
            p['hp'] = min(p['max_hp'], p['hp'] + amount)
            result['hp'] = p['hp']
        elif btype == 'weapon':
            result['weapon'] = data.get('weaponKey', 'pistol')
            p['weapon'] = result['weapon']
        elif btype == 'turret':
            tx = float(data.get('x', SAFE_X))
            ty = float(data.get('y', SAFE_Y))
            tx = max(40, min(WORLD_W - 40, tx))
            ty = max(40, min(WORLD_H - 40, ty))
            gs['enemy_id_counter'] += 1
            gs['turrets'].append({
                'id': f't{gs["enemy_id_counter"]}',
                'x': tx, 'y': ty,
                'hp': 80, 'max_hp': 80,
                'last_fire': 0,
            })
        emit('buy_result', result)

@socketio.on('gamble')
def on_gamble():
    sid = request.sid
    with game_lock:
        if sid not in game_state['players']:
            return
        p = game_state['players'][sid]
        if p['money'] < 50:
            return
        effect_id = random.choice(EFFECTS)
    emit('effect_applied', {'id': sid, 'effectId': effect_id})

@socketio.on('chat')
def on_chat(data):
    sid = request.sid
    with game_lock:
        if sid not in game_state['players']:
            return
        nick = game_state['players'][sid]['nick']
    text = str(data.get('text', ''))[:100]
    socketio.emit('chat_msg', {'nick': nick, 'text': text})

# ─── ВОЛНЫ И ИГРОВАЯ ЛОГИКА ──────────────────────────────────────
def start_next_wave():
    gs = game_state
    gs['wave'] += 1
    gs['wave_active'] = True
    gs['wave_breather'] = False
    gs['enemies'] = []
    gs['wave_killed'] = 0
    wave = gs['wave']
    base_count = 5 + wave * 3
    is_boss_wave = (wave % 5 == 0)
    gs['wave_enemy_count'] = base_count + (1 if is_boss_wave else 0)
    socketio.emit('wave_start', {'wave': wave})
    for i in range(base_count):
        delay = i * max(0.2, 0.8 - wave * 0.02)
        etype = choose_enemy_type(wave)
        threading.Timer(delay, spawn_enemy_delayed, args=[etype, False]).start()
    if is_boss_wave:
        threading.Timer(base_count * 0.4 + 1.0, spawn_enemy_delayed, args=['boss', True]).start()

def spawn_enemy_delayed(etype, is_boss):
    with game_lock:
        if not game_state['wave_active'] or game_state['game_over']:
            return
        enemy = new_enemy(etype, game_state['wave'], is_boss)
        game_state['enemies'].append(enemy)

def trigger_game_over():
    gs = game_state
    gs['game_over'] = True
    gs['wave_active'] = False
    socketio.emit('state_update', get_serializable_state())

def update_enemies(dt, now):
    gs = game_state
    for e in gs['enemies']:
        if e.get('dead', False):
            continue
        if e.get('is_boss', False):
            update_boss_ability(e, now)
        tx, ty = find_target(e)
        move_enemy(e, tx, ty, dt)
        e['x'] = max(e['radius'], min(WORLD_W - e['radius'], e['x']))
        e['y'] = max(e['radius'], min(WORLD_H - e['radius'], e['y']))
        d_safe = dist(e['x'], e['y'], SAFE_X, SAFE_Y)
        safe_edge = (SAFE_W / 2 + SAFE_H / 2) / 2 + e['radius']
        if d_safe < safe_edge + e['attack_range']:
            if now - e['last_attack'] > e['attack_rate']:
                e['last_attack'] = now
                dmg = e['damage']
                gs['safe_hp'] = max(0, gs['safe_hp'] - dmg)
                socketio.emit('safe_hit', {'hp': gs['safe_hp'], 'dmg': round(dmg, 1)})
                if gs['safe_hp'] <= 0:
                    trigger_game_over()
                if e['type'] == 'bomber':
                    e['dead'] = True
                    gs['wave_killed'] += 1
                    handle_bomber_explosion(e)
        if e['type'] == 'shooter' or e.get('is_boss', False):
            shoot_nearest_player(e, now)

def move_enemy(e, tx, ty, dt):
    dx, dy = tx - e['x'], ty - e['y']
    d = math.sqrt(dx*dx + dy*dy)
    if d < 2:
        return
    spd = e['speed']
    e['x'] += (dx / d) * spd * dt * 60
    e['y'] += (dy / d) * spd * dt * 60

def find_target(e):
    gs = game_state
    d_safe = dist(e['x'], e['y'], SAFE_X, SAFE_Y)
    if e['type'] in ('bomber', 'heavy') and d_safe < 350:
        return SAFE_X, SAFE_Y
    if d_safe < 500:
        return SAFE_X, SAFE_Y
    best_sid, best_d = None, float('inf')
    for sid, p in gs['players'].items():
        if p.get('dead', False):
            continue
        d = dist(e['x'], e['y'], p['x'], p['y'])
        if d < best_d:
            best_d = d
            best_sid = sid
    if best_sid:
        p = gs['players'][best_sid]
        return p['x'], p['y']
    return SAFE_X, SAFE_Y

def shoot_nearest_player(e, now):
    gs = game_state
    shoot_range = e.get('shoot_range', 260)
    shoot_rate = e.get('shoot_rate', 1.2)
    if now - e['last_shot'] < shoot_rate:
        return
    best_sid, best_d = None, float('inf')
    for sid, p in gs['players'].items():
        if p.get('dead', False):
            continue
        d = dist(e['x'], e['y'], p['x'], p['y'])
        if d < shoot_range and d < best_d:
            best_d = d
            best_sid = sid
    if best_sid:
        e['last_shot'] = now
        p = gs['players'][best_sid]
        dmg = int(e['damage'] * (0.4 if e.get('is_boss') else 1.0))
        hit_player(best_sid, dmg)

def hit_player(sid, dmg):
    gs = game_state
    if sid not in gs['players']:
        return
    p = gs['players'][sid]
    if p.get('dead', False):
        return
    p['hp'] -= dmg
    socketio.emit('player_hit', {'id': sid, 'hp': p['hp'], 'dmg': dmg})
    if p['hp'] <= 0:
        kill_player(sid)

def kill_player(sid):
    gs = game_state
    if sid not in gs['players']:
        return
    p = gs['players'][sid]
    p['dead'] = True
    p['hp'] = 0
    threading.Timer(5.0, respawn_player, args=[sid]).start()

def respawn_player(sid):
    with game_lock:
        gs = game_state
        if sid not in gs['players']:
            return
        p = gs['players'][sid]
        p['dead'] = False
        p['hp'] = 50
        p['x'] = SAFE_X + random.randint(-40, 40)
        p['y'] = SAFE_Y + 100

def update_boss_ability(boss, now):
    if now - boss.get('last_ability', 0) < 8.0:
        return
    boss['last_ability'] = now
    abilities = boss.get('abilities', [])
    if not abilities:
        return
    ab = random.choice(abilities)
    gs = game_state
    if ab == 'minions':
        for _ in range(3):
            minion = new_enemy('grunt', gs['wave'])
            angle = random.uniform(0, math.pi * 2)
            minion['x'] = boss['x'] + math.cos(angle) * 60
            minion['y'] = boss['y'] + math.sin(angle) * 60
            gs['enemies'].append(minion)
            gs['wave_enemy_count'] += 1
    elif ab == 'teleport':
        pos = get_spawn_pos()
        boss['x'] = pos['x']
        boss['y'] = pos['y']
    elif ab == 'shield':
        boss['shield'] = True
        boss['shield_hp'] = 300
    elif ab == 'regen':
        boss['hp'] = min(boss['max_hp'], boss['hp'] + int(boss['max_hp'] * 0.2))
    elif ab == 'slow_aura':
        boss['slow_aura'] = True
    elif ab == 'ranged_attack':
        for sid, p in gs['players'].items():
            if p.get('dead'):
                continue
            if dist(boss['x'], boss['y'], p['x'], p['y']) < 350:
                hit_player(sid, int(boss['damage'] * 0.4))

def update_turrets(dt, now):
    gs = game_state
    turret_rate = 0.8
    turret_range = 200
    turret_dmg = 18
    for t in gs['turrets']:
        if now - t['last_fire'] < turret_rate:
            continue
        nearest = None
        nearest_d = float('inf')
        for e in gs['enemies']:
            if e.get('dead'):
                continue
            d = dist(t['x'], t['y'], e['x'], e['y'])
            if d < turret_range and d < nearest_d:
                nearest_d = d
                nearest = e
        if nearest:
            t['last_fire'] = now
            apply_enemy_damage(nearest, turret_dmg, None)

# ─── ИГРОВОЙ ТИК ───────────────────────────────────────────────
def game_tick():
    while True:
        time.sleep(TICK_INTERVAL)
        with game_lock:
            gs = game_state
            if gs['game_over'] or not gs['players']:
                continue
            now = time.time()
            dt = min(TICK_INTERVAL * 2, now - gs['last_tick'])
            gs['last_tick'] = now

            if gs['wave_breather']:
                gs['breather_timer'] -= dt
                if gs['breather_timer'] <= 0:
                    gs['wave_breather'] = False
                    start_next_wave()
                continue

            if not gs['wave_active']:
                continue

            update_enemies(dt, now)
            update_turrets(dt, now)

            alive = [e for e in gs['enemies'] if not e.get('dead', False)]
            gs['enemies'] = alive
            if len(alive) == 0 and gs['wave_killed'] >= gs['wave_enemy_count'] - 1:
                gs['wave_active'] = False
                gs['wave_breather'] = True
                gs['breather_timer'] = BREATHER_DURATION
                socketio.emit('wave_end', {})

            socketio.emit('state_update', get_serializable_state())

# ─── ЗАПУСК ────────────────────────────────────────────────────
if __name__ == '__main__':
    # Игровой тик в отдельном потоке
    threading.Thread(target=game_tick, daemon=True).start()
    print('[SERVER] Game tick loop started')

    # Запуск сервера в главном потоке
    def start_server():
        print('[SERVER] Starting Flask-SocketIO on port 5000...')
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    # Даём серверу время подняться
    time.sleep(1)

    # Ngrok туннель
    try:
        from pyngrok import ngrok
        ngrok.set_auth_token("3EUAvxvni84EnyW0BHobb1cf9s1_22w1T2dnp1UrHno7Ez6G9")   # ← ВСТАВЬТЕ СВОЙ ТОКЕН
        tunnel = ngrok.connect(5000, 'http')  # порт 5000
        print(f'📡 Публичный URL: {tunnel.public_url}')
    except Exception as e:
        print(f'[NGROK] Ошибка: {e}')

    print('Сервер работает. Остановите вручную (Ctrl+C).')
    server_thread.join()