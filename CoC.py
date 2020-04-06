#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib

import numpy as np
import pandas as pd

import apikeys

hdr = apikeys.hdr

class currentWar():
    def __init__(self, tag):
        self.tag = tag
        self.public = public_warlog(tag)
        if not self.public:
            raise ValueError("Clan's warlog is not public.")
        url = f"https://api.clashofclans.com/v1/clans/%23{tag}/currentwar"
        req = urllib.request.Request(url, headers=hdr)
        self.response = json.loads(urllib.request.urlopen(req).read())
        if self.response["state"] == "notInWar":
            raise ValueError("Not in war.")
        self.clantag = self.response["clan"]["tag"].replace("#", "")
        self.ok, self.clan_members = clan_members(self.clantag)

    def compare(self, inverti=False):
        if not inverti:
            if not (hasattr(self, 'indexesClan') and hasattr(self, 'indexesOpponnent')):
                clanMemberStat = self.getIndexesClan()
                opponentMemberStat = self.getIndexesOpponent()
            else:
                clanMemberStat = self.indexesClan
                opponentMemberStat = self.indexesOpponent
        else:
            if not (hasattr(self, 'indexesClan') and hasattr(self, 'indexesOpponnent')):
                opponentMemberStat = self.getIndexesClan()
                clanMemberStat = self.getIndexesOpponent()
            else:
                opponentMemberStat = self.indexesClan
                clanMemberStat = self.indexesOpponent

        df = (clanMemberStat.drop(["name", "tag"], axis=1) / opponentMemberStat.drop(["name", "tag"], axis=1)) - 1
        df.trophies = df.trophies / 10
        df["index"] = df.sum(axis=1)
        df.index = clanMemberStat.name
        self.conf = df
        return df

    def getClanAttackIndexes(self):
        if not self.ok:
            return None
        if self.response["state"] != "inWar":
            raise ValueError("Not in war.")
        if hasattr(self, 'indexesClan'):
            clan = self.indexesClan.copy()
        else:
            clan = self.getIndexesClan().copy()
        if hasattr(self, 'indexesOpponent'):
            opponent = self.indexesOpponent.copy()
        else:
            opponent = self.getIndexesOpponent().copy()
        clan.index = clan.tag
        opponent.index = opponent.tag
        clanstats_ = self.getClanMembersStats().copy()
        clanstats = pd.DataFrame(list(np.hstack(clanstats_.attacks)))
        clanValues = clan.loc[clanstats.attackerTag].drop(["name", "tag"], axis=1).reset_index(drop=True)
        opponentValues =  opponent.loc[clanstats.defenderTag].drop(["name", "tag"], axis=1).reset_index(drop=True)
        indexes = clanValues / opponentValues - 1
        indexes.index = clanstats.attackerTag
        return indexes

    def getClanAttacks(self):
        if self.response["state"] != "inWar":
            raise ValueError("Not in war.")
        clanstats_ = self.getClanMembersStats().copy()
        return pd.DataFrame(list(np.hstack(clanstats_.attacks)))

    def getOpponentAttacks(self):
        if self.response["state"] != "inWar":
            raise ValueError("Not in war.")
        opponentstats_ = self.getOpponentMembersStats().copy()
        return pd.DataFrame(list(np.hstack(opponentstats_.attacks)))

    def getClanMembers(self):
        df = pd.DataFrame(
            self.response["clan"]["members"]
            ).sort_values(by=["mapPosition"]).reset_index(drop=True)
        df.fillna("", inplace=True)
        if self.response["state"] == "inWar":
            df["NAttacks"] =  [len(attack) for attack in df.attacks]
        return df

    def getClanMembersStats(self):
        df_clan = self.getClanMembers()
        df_users = self.clan_members
        if not self.ok:
            return None
        df_users.index = df_users.tag
        return pd.concat(
            [
                df_clan, 
                df_users.loc[df_clan.tag][["expLevel", "trophies"]].reset_index(drop=True)
                ], 
            axis=1, 
            sort=False
            )

    def getIndexesClan(self):
        clanMemberStat = self.getClanMembersStats()
        if hasattr(self, 'troopsClanLevel'):
            weightsTroopsMember = self.troopsClanLevel
        else:
            weightsTroopsMember = self.getClanTroopsLevel()
        df = clanMemberStat[["tag", "name", "townhallLevel", "expLevel", "trophies"]]
        df["troops"] = weightsTroopsMember
        self.indexesClan = df
        return df

    def getIndexesOpponent(self):
        opponentMemberStat = self.getOpponentMembersStats()
        if hasattr(self, 'troopsOpponentLevel'):
            weightsTroopsOpponent = self.troopsOpponentLevel
        else:
            weightsTroopsOpponent = self.getOpponentTroopsLevel()
        df = opponentMemberStat[["tag", "name", "townhallLevel", "expLevel", "trophies"]]
        df["troops"] = weightsTroopsOpponent
        self.indexesOpponnent = df
        return df

    def getClanTroopsLevel(self):
        clanMemberStat = self.getClanMembersStats()
        weightsTroopsClan = []
        for member in clanMemberStat.tag:
            ut = User(member.replace("#", ""))
            weightsTroopsClan.append(ut.getTroops().level.sum() + ut.getSpells().level.sum() + ut.getHeroes().level.sum())
        self.troopsClanLevel = weightsTroopsClan
        return weightsTroopsClan

    def getOpponentTroopsLevel(self):
        opponentMemberStat = self.getOpponentMembersStats()
        weightsTroopsOpponent = []
        for member in opponentMemberStat.tag:
            ut = User(member.replace("#", ""))
            weightsTroopsOpponent.append(ut.getTroops().level.sum() + ut.getSpells().level.sum() + ut.getHeroes().level.sum())
        self.troopsOpponentLevel = weightsTroopsOpponent
        return weightsTroopsOpponent

    def getBetterOrder(self):
        if hasattr(self, 'indexesClan'):
            clan = self.indexesClan.copy()
        else:
            clan = self.getIndexesClan().copy()
        clan.trophies = clan.trophies / 200
        clan.townhallLevel = clan.townhallLevel * 10
        clan["index"] = clan.sum(axis=1)

        if hasattr(self, 'indexesOpponent'):
            opponent = self.indexesOpponent.copy()
        else:
            opponent = self.getIndexesOpponent().copy()
        opponent.trophies = opponent.trophies / 200
        opponent.townhallLevel = opponent.townhallLevel * 10
        opponent["index"] = opponent.sum(axis=1)

        clan_ = clan.copy()
        res = []
        for valore in opponent.sort_values(by=["index"], ascending=False)[["index", "name"]].values:
            rapp = clan_.index / valore[0]
            res.append((valore[1], rapp.max() - 1, clan.name.loc[rapp.idxmax()]))
            clan_.drop(rapp.idxmax(), inplace=True)

        df =  pd.DataFrame(res, columns = ["Defender", "Index", "Attacker"])[["Attacker", "Index", "Defender"]]
        df.index = df.Attacker
        self.betterOrder = df
        return df

    def getOpponentMembers(self):
        df = pd.DataFrame(
            self.response["opponent"]["members"]
            ).sort_values(by=["mapPosition"]).reset_index(drop=True)
        df.fillna("", inplace=True)
        if self.response["state"] != "preparation":
            df["NAttacks"] =  [len(attack) for attack in df.attacks]
        return df

    def getOpponentMembersStats(self):
        tag = self.response["opponent"]["tag"].replace("#", "")
        df_clan = self.getOpponentMembers()
        ok, df_users = clan_members(tag)
        if not ok:
            return None
        df_users.index = df_users.tag
        return pd.concat(
            [
                df_clan, 
                df_users.loc[df_clan.tag][["expLevel", "trophies"]].reset_index(drop=True)
                ], 
            axis=1, 
            sort=False
            )

    def getResponse(self):
        return self.response

    def getStatOpponent(self):
        tag = self.response["opponent"]["tag"].replace("#", "")
        ok, df_warlog = warlog(tag)
        if not ok:
            return None
        return df_warlog

    def plotBetterOrder(self):
        if hasattr(self, 'betterOrder'):
            return self.betterOrder.Index.plot(kind="barh")
        return self.getBetterOrder().Index.plot(kind="barh")

    def plotClanAttack(self):
        attIdx = self.getClanAttackIndexes().copy()
        attIdx["Index"] = attIdx.sum(axis=1)
        clMem = self.getClanMembers()
        clMem.index = clMem.tag
        attIdx.index = clMem.loc[attIdx.index].name
        return attIdx.Index.plot(kind="barh")

    def plotCompare(self, inverti=False):
        if hasattr(self, 'conf'):
            return self.conf.index.plot(kind="barh")
        return self.compare(inverti).index.plot(kind="barh")

class User():
    def __init__(self, tag):
        self.tag = tag
        url = f"https://api.clashofclans.com/v1/players/%23{tag}"
        req = urllib.request.Request(url, headers=hdr)
        self.response = json.loads(urllib.request.urlopen(req).read())

    def getHeroes(self, selected="home"):
        """ selected = "home" / "builderBase"
        """
        df = pd.DataFrame(self.response["heroes"])
        return df[df.village == selected]

    def getResponse(self):
        return self.Response

    def getSpells(self, selected="home"):
        """ selected = "home" / "builderBase"
        """
        df = pd.DataFrame(self.response["spells"])
        return df[df.village == selected]

    def getTroops(self, selected="home"):
        """ selected = "home" / "builderBase"
        """
        df = pd.DataFrame(self.response["troops"])
        return df[df.village == selected]

def data_user(tag):
    url = f"https://api.clashofclans.com/v1/players/%23{tag}"
    req = urllib.request.Request(url, headers=hdr)
    try:
        response = urllib.request.urlopen(req).read()
    except Exception as e:
        return False, e
    return True, pd.DataFrame(json.loads(response)["memberList"])

def clan_members(tag):
    """ Return pandas.DataFrame with clan members
    """
    url = f"https://api.clashofclans.com/v1/clans/%23{tag}"
    req = urllib.request.Request(url, headers=hdr)
    try:
        response = urllib.request.urlopen(req).read()
    except Exception as e:
        return False, e
    return True, pd.DataFrame(json.loads(response)["memberList"])

def public_warlog(tag):
    """ Is warlog public?
        return (? error), Bool
    """
    url = f"https://api.clashofclans.com/v1/clans/%23{tag}"
    req = urllib.request.Request(url, headers=hdr)
    try:
        response = urllib.request.urlopen(req).read()
    except Exception as e:
        return False, e
    return True, json.loads(response)["isWarLogPublic"]

def warlog(tag):
    url = f"https://api.clashofclans.com/v1/clans/%23{tag}/warlog"
    req = urllib.request.Request(url, headers=hdr)
    try:
        response = urllib.request.urlopen(req).read()
    except Exception as e:
        return False, e
    df = pd.DataFrame(json.loads(response)["items"])
    df = df[np.array([len(a) for a in df.opponent])== 6]
    df["clantag"] = [a["tag"] for a in df.clan]
    df["opponenttag"] = [a["tag"] for a in df.opponent]
    df.result = df.result == "win"
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    return True, df

def getwar(tag):
    """ tag: String, war's tag
    """
    url = f"/clanwarleagues/wars/{warTag}"
    req = urllib.request.Request(url, headers=hdr)
    try:
        response = urllib.request.urlopen(req).read()
    except Exception as e:
        return False, e
    return True, pd.DataFrame(json.loads(response))


def indexFromPickle(clan, opponent):
    """ Read database
    """
    clanAtt = pd.DataFrame(list(np.hstack(clan[clan.attacks != ""].attacks)))
    opponentAtt = pd.DataFrame(list(np.hstack(opponent[opponent.attacks != ""].attacks)))
    clan.index = clan.tag
    opponent.index = opponent.tag
    clanStat = pd.concat(
        [
            clanAtt, 
            (clan.loc[clanAtt.attackerTag][["name", "townhallLevel", "expLevel", "trophies"]]).reset_index(drop=True)
        ],
         axis=1)
    opponentStat = pd.concat(
        [
            opponentAtt, 
            (opponent.loc[opponentAtt.attackerTag][["name", "townhallLevel", "expLevel", "trophies"]]).reset_index(drop=True)
        ],
         axis=1)

    if "troops" not in clanStat.columns:
        weightsTroopsClan = []
        for member in clanStat.attackerTag.unique():
            ut = User(member.replace("#", ""))
            weightsTroopsClan.append(ut.getTroops().level.sum() + ut.getSpells().level.sum() + ut.getHeroes().level.sum())
        weightsTroopsClan = pd.Series(weightsTroopsClan)
        weightsTroopsClan.index = clanStat.attackerTag.unique()
        clanStat["troops"] =  (weightsTroopsClan.loc[clanStat.attackerTag]).reset_index(drop=True)

    if "troops" not in opponentStat.columns:
        weightsTroopsOpponent = []
        for member in opponentStat.attackerTag.unique():
            ut = User(member.replace("#", ""))
            weightsTroopsOpponent.append(ut.getTroops().level.sum() + ut.getSpells().level.sum() + ut.getHeroes().level.sum())
        weightsTroopsOpponent = pd.Series(weightsTroopsOpponent)
        weightsTroopsOpponent.index = opponentStat.attackerTag.unique()
        opponentStat["troops"] = (weightsTroopsOpponent.loc[opponentStat.attackerTag]).reset_index(drop=True)

    return clanStat, opponentStat
    
    


