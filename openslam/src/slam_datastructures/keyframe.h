#pragma once
#include <vector>
#include <Eigen/Eigen>
#include <opencv2/core.hpp>
#include <pybind11/pybind11.h>
#include "types.h"
namespace py = pybind11;
namespace cslam
{
class Frame;
class Landmark;
class KeyFrame
{
public:
    EIGEN_MAKE_ALIGNED_OPERATOR_NEW
    KeyFrame() = delete;
    KeyFrame(const size_t kf_id, const Frame& frame);
    size_t kf_id_;
    const size_t src_frm_id_;
    const std::string im_name_;
    //! keypoints of monocular or stereo left image
    const std::vector<cv::KeyPoint> keypts_;
    //! undistorted keypoints of monocular or stereo left image
    const std::vector<cv::KeyPoint> undist_keypts_;
    std::vector<Landmark*> get_valid_lms();
    std::vector<size_t> get_valid_idx() const;
    //! bearing vectors
    const std::vector<Eigen::Vector3f, Eigen::aligned_allocator<Eigen::Vector3f>> bearings_;
    
    //! keypoint indices in each of the cells
    const std::vector<std::vector<std::vector<unsigned int>>> keypts_indices_in_cells_;
    //! descriptors
    const cv::Mat descriptors_;
    std::vector<Landmark*> landmarks_;
    
    Eigen::Vector3f get_obs_by_idx(const size_t idx) const
    {
        const auto kpt = keypts_[idx];
        return Eigen::Vector3f(kpt.pt.x, kpt.pt.y, kpt.size);
    }
    
    Eigen::Matrix4f get_Twc() const { return T_wc; }
    
    void set_Twc(const Eigen::Matrix4f& T_wc_)
    {
        T_wc = T_wc_;
        T_cw = T_wc.inverse();
        cam_center_ = T_wc.block<3,1>(0,3);
    }
    
    void set_Tcw(const Eigen::Matrix4f& T_cw_)
    {
        T_cw = T_cw_;
        T_wc = T_cw_.inverse();
        cam_center_ = T_wc.block<3,1>(0,3);
    }

    //The way it looks, this is the world pose
    Eigen::Matrix4f get_Tcw() const { return T_cw; }
    Eigen::Vector3f get_cam_center() const { return cam_center_; }
    Eigen::Matrix3f get_rotation() const { return T_cw.block<3,3>(0,0); }
    Eigen::Vector3f get_translation() const { return T_cw.block<3,1>(0,3); }
    // ORB scale pyramid information
    //! number of scale levels
    size_t num_scale_levels_;
    //! scale factor
    float scale_factor_;
    //! log scale factor
    float log_scale_factor_;
    //! list of scale factors
    const std::vector<float> scale_factors_;
    //! list of inverse of scale factors
    const std::vector<float> inv_scale_factors_;
    //! list of sigma^2 (sigma=1.0 at scale=0) for optimization
    const std::vector<float> level_sigma_sq_;
    //! list of 1 / sigma^2 for optimization
    const std::vector<float> inv_level_sigma_sq_;
    py::object get_valid_keypts() const;
    
    void add_landmark(Landmark* lm, const size_t idx);
    size_t get_num_tracked_lms(const size_t min_num_obs_thr) const;
    // basically store_new_keyframe
    // std::vector<Landmark*> update_lms_after_kf_insert();
    void erase_landmark_with_index(const unsigned int idx) 
    {
        // std::lock_guard<std::mutex> lock(mtx_observations_);
        landmarks_.at(idx) = nullptr;
    }
    float compute_median_depth(const bool abs) const;
    py::object getKptsUndist() const;
    py::object getKptsPy() const;
    py::object getDescPy() const;

    const size_t num_keypts_;
    /**
     * Erase a landmark observed by myself at keypoint idx
     */
    void erase_landmark_with_index(const size_t idx)
    {
        landmarks_.at(idx) = nullptr;
    }

    std::vector<size_t> compute_local_keyframes() const;

    /**
     * Replace the landmark
     */
    void replace_landmark(Landmark* lm, const size_t idx)
    {
        landmarks_.at(idx) = lm;
    }

    void apply_landmark_replace();
private:
    Eigen::Matrix4f T_wc; // camera to world transformation, pose
    Eigen::Matrix4f T_cw; // world to camera transformation
    Eigen::Vector3f cam_center_;

};
}