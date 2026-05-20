(ns actors.math-test
  (:require [clojure.test :refer :all]
            [actors.math :refer :all]))

(deftest test-mean
  (testing "Mean of a list of numbers"
    (is (= 3 (mean [1 2 3 4 5])))
    (is (= 5.0 (mean [5.0])))
    (is (= 0 (mean [-1 0 1]))))

  (testing "Mean of floats"
    (is (< (Math/abs (- 2.5 (mean [1.0 2.0 3.0 4.0]))) 0.0001))))

(deftest test-standard-deviation
  (testing "Standard deviation of a list"
    (is (> (standard-deviation [1 2 3 4 5]) 0))
    (is (= 0 (standard-deviation [5 5 5 5]))))

  (testing "Higher spread yields higher standard deviation"
    (is (> (standard-deviation [1 5 9 13])
           (standard-deviation [4 5 6 7])))))

(deftest test-correlation
  (testing "Perfect positive correlation"
    (let [x [1 2 3 4 5]
          y [2 4 6 8 10]]
      (is (< (Math/abs (- 1.0 (correlation x y))) 0.0001))))

  (testing "Perfect negative correlation"
    (let [x [1 2 3 4 5]
          y [10 8 6 4 2]]
      (is (< (Math/abs (- -1.0 (correlation x y))) 0.0001))))

  (testing "Zero correlation for constant series"
    (let [x [1 2 3]
          y [5 5 5]]
      (is (= 0 (correlation x y))))))

(deftest test-linear-regression
  (testing "Linear regression returns slope and intercept"
    (let [x [1 2 3 4 5]
          y [2 4 6 8 10]
          result (linear-regression x y)]
      (is (contains? result :slope))
      (is (contains? result :intercept))
      (is (< (Math/abs (- 2.0 (:slope result))) 0.0001))
      (is (< (Math/abs (- 0.0 (:intercept result))) 0.0001))))

  (testing "Regression with y-intercept"
    (let [x [1 2 3 4 5]
          y [3 5 7 9 11]
          result (linear-regression x y)]
      (is (< (Math/abs (- 2.0 (:slope result))) 0.0001))
      (is (< (Math/abs (- 1.0 (:intercept result))) 0.0001)))))
