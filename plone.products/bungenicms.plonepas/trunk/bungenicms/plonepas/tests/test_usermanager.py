
# tests from sqlpasplugin ( GPL v2 )

from bungenicms.plonepas.tests import basetestcase

class TestUserManager(basetestcase.BaseTestCase):

    def afterSetUp(self):
        self.username = 'joe'
        self.password = 'password'
        self.plugin = self.getPAS()['bungeni_users']

    def testDoAddUser(self):
        self.plugin.doAddUser(self.username, self.password)
        ret = self.plugin.enumerateUsers(id=self.username, exact_match=True)
        self.assertEqual(len(ret), 1)

    def testRemoveUser(self):
        ret = self.plugin.enumerateUsers(id=self.username, exact_match=True)
        self.assertEqual(len(ret), 0)
        self.plugin.doAddUser(self.username, self.password)
        self.plugin.removeUser(self.username)
        ret = self.plugin.enumerateUsers(id=self.username, exact_match=True)
        self.assertEqual(len(ret), 0)

    def testAuthenticateCredentials(self):
        auth = self.plugin.authenticateCredentials({'login': self.username,
                                                          'password': self.password})
        self.assertEqual(auth, None)

        self.plugin.doAddUser(self.username, self.password)
        auth = self.plugin.authenticateCredentials({'login': self.username,
                                                          'password': self.password})
        self.assertEqual(auth, (self.username, self.username))


class TestEnumerateUsers(basetestcase.BaseTestCase):

    def afterSetUp(self):
        self.plugin = self.getPAS()['bungeni_users']
        self.plugin.doAddUser('user_1', 'password')
        self.plugin.doAddUser('user_2', 'password')
        self.plugin.doAddUser('foo_user_1', 'password')
        self.plugin.doAddUser('bar', 'password')

    def testNoIdAndNoLoginNoExact(self):
        ret = self.plugin.enumerateUsers()
        self.assertEqual(len(ret), 4)

    def testNoIdAndNoLoginExact(self):
        ret = self.plugin.enumerateUsers(exact_match=True)
        self.assertEqual(len(ret), 0)

    def testReturnFormat(self):
        ret = self.plugin.enumerateUsers(id='user_1', exact_match=True)
        expected = (dict(login='user_1', id= 'user_1', pluginid='bungeni_users'),)
        #self.assertEqual( ret, expected )
        
        self.assertEqual(len(ret), len(expected))
        self.assertEqual( ret[0]['login'], expected[0]['login'])
        self.assertEqual( ret[0]['id'], expected[0]['id'])
        self.assertEqual( ret[0]['pluginid'], expected[0]['pluginid'])

    def testIdStringNoExact(self):
        ret = self.plugin.enumerateUsers(id='user_1')
        self.assertEqual(len(ret), 2) # user_1, foo_user_1

    def testIdEqualLogin(self):
        ret = self.plugin.enumerateUsers(id='user_1', login='user_1')
        self.assertEqual(len(ret), 2) # user_1, foo_user_1

    def testLoginStringExact(self):
        ret = self.plugin.enumerateUsers(login='user', exact_match=True)
        self.assertEqual(ret, [])

    def testLoginStringNoExact(self):
        ret = self.plugin.enumerateUsers(login='user')
        self.assertEqual(len(ret), 3) # all but bar

    def testLoginListExact(self):
        ret = self.plugin.enumerateUsers(login=['user_1', '2'], exact_match=True)
        self.assertEqual(len(ret), 1) # user_1

    def testLoginListNoExact(self):
        ret = self.plugin.enumerateUsers(login=['user_0', '2'])
        self.assertEqual(len(ret), 1) # user_2

    def testIdListExact(self):
        ret = self.plugin.enumerateUsers(id=['user_1', 'foo'], exact_match=True)
        self.assertEqual(len(ret), 1) # user_1

    def testIdListNoExact(self):
        ret = self.plugin.enumerateUsers(id=['user_1', 'foo'])
        self.assertEqual(len(ret), 2) # user_1, foo_user_11

    def testIdStringAndLoginStringNoExact(self):
        ret = self.plugin.enumerateUsers(id='user_1', login='bar')
        self.assertEqual(len(ret), 3) # user_1, foo_user_11, bar

    def testIdStringAndLoginStringExact(self):
        ret = self.plugin.enumerateUsers(id='user', login='bar', exact_match=True)
        self.assertEqual(len(ret), 1) # bar

    def testIdListAndLoginStringNoExact(self):
        ret = self.plugin.enumerateUsers(id=['2', '3'], login='4')
        self.assertEqual(len(ret), 1) # user_2

    def testIdStringAndLoginListNoExact(self):
        ret = self.plugin.enumerateUsers(id='5', login=['0', '2', '8'])
        self.assertEqual(len(ret), 1) # user_2

    def testMaxResultsZero(self):
        ret = self.plugin.enumerateUsers(max_results=0)
        self.assertEqual(len(ret), 0)

    def testMaxResultsFixed(self):
        ret = self.plugin.enumerateUsers(max_results=3)
        self.assertEqual(len(ret), 3)

    def testMaxResultsAbove(self):
        ret = self.plugin.enumerateUsers(max_results=10)
        self.assertEqual(len(ret), 4)


def test_suite( ):
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUserManager))
    suite.addTest(makeSuite(TestEnumerateUsers))
    return suite
        
