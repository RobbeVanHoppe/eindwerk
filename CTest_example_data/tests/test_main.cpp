#include <gtest/gtest.h>

namespace RP_TestProject {

    // Test case 1: Passes
    TEST(BasicAssertions, AssertTrue) {
        EXPECT_TRUE(true);
    }

    // Test case 2: Fails
    TEST(BasicAssertions, AssertFalse) {
        EXPECT_FALSE(true);
    }

    // Test case 3: Fails because expected value does not match actual value
    TEST(FailureScenarios, MismatchedValues) {
        int expected = 10;
        int actual = 5;
        EXPECT_EQ(expected, actual);
    }

    // Test case 4: Fails because function throws an exception
    TEST(FailureScenarios, UnexpectedException) {
        EXPECT_THROW({
            throw std::runtime_error("Unexpected exception");
        }, std::logic_error);
    }

    // Test case 5: Fails because function does not throw expected exception
    TEST(FailureScenarios, NoExpectedException) {
        EXPECT_THROW({
            // No exception thrown here
        }, std::runtime_error);
    }

    // Test case 6: Passes with a warning
    TEST(WarningScenarios, WarningScenario) {
        EXPECT_TRUE(true) << "This test passed, but with a warning message.";
    }

    // Test case 7: Skipped test
    TEST(SkippedScenarios, SkippedTest) {
        GTEST_SKIP() << "This test is skipped.";
        EXPECT_TRUE(false);
    }

    // Test case 8: Fails with a custom failure message
    TEST(FailureScenarios, CustomFailureMessage) {
        EXPECT_TRUE(false) << "This test failed with a custom failure message.";
    }

    // Test case 9: Passes after a retry
    TEST(RetryScenarios, RetrySuccess) {
        static int attempt = 0;
        if (attempt < 1) {
            attempt++;
            EXPECT_TRUE(false) << "This test failed on the first attempt.";
        } else {
            EXPECT_TRUE(true);
        }
    }

    // Test case 10: Fails after a retry
    TEST(RetryScenarios, RetryFailure) {
        static int attempt = 0;
        if (attempt < 1) {
            attempt++;
            EXPECT_TRUE(false) << "This test failed on the first attempt.";
        } else {
            EXPECT_TRUE(false) << "This test also failed on the second attempt.";
        }
    }

} // namespace RP_TestProject

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}