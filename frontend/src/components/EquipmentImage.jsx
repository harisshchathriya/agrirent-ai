import { useState } from "react";
import { FaTractor } from "react-icons/fa";
import { shouldShowEquipmentImage } from "../utils/equipmentPresentation";

export default function EquipmentImage({
  src,
  alt,
  className = "",
  iconClassName = "text-6xl text-emerald-700",
  containerClassName = "",
}) {
  const [failedSrc, setFailedSrc] = useState("");

  return (
    <div
      className={`flex items-center justify-center overflow-hidden bg-gradient-to-br from-emerald-50 via-lime-50 to-amber-50 ${containerClassName}`}
    >
      {shouldShowEquipmentImage(src, failedSrc) ? (
        <img
          src={src}
          alt={alt}
          className={`h-full w-full object-cover ${className}`}
          onError={() => setFailedSrc(src)}
        />
      ) : (
        <FaTractor className={iconClassName} />
      )}
    </div>
  );
}
